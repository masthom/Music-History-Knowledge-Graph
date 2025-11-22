#!/usr/bin/env python3
# coding: utf-8
"""
Robustes Skript: liest TTL, extrahiert rowClasses und rowForms (mehrere Schreibweisen)
und findet rowClasses, deren rowForms rotationsäquivalent sind.
Ausgabe:
 - rotation_groups.txt  (Gruppen von rowClasses)
 - rotation_pairs.txt   (konkrete Form-Paare mit Shift)
"""

import re
from collections import defaultdict

INPUT_TTL = "MusicHistoryGraph_TwelveToneMusic_CompleteAdjust.ttl"        # <-- hier Datei ändern
OUT_GROUPS = "rotation_groups.txt"
OUT_PAIRS = "rotation_pairs.txt"

# -------------------------
# Hilfsfunktionen
# -------------------------
IRI_RE = re.compile(r"mhg:(\d+(?:_\d+)*)")

def to_list_from_iri(iri: str):
    """mhg:1_2_3 -> [1,2,3]"""
    m = IRI_RE.match(iri)
    if not m:
        return None
    return [int(x) for x in m.group(1).split("_")]

def is_rotation(a, b):
    """Check if list b is a rotation of list a."""
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    if len(a) < 3:   # ignore too short per spec
        return False
    doubled = a + a
    L = len(a)
    for start in range(L):
        if doubled[start:start+L] == b:
            return True
    return False

def rotation_shift(a, b):
    """If b is rotation of a, return shift k such that b == a[k:]+a[:k], else None."""
    if len(a) != len(b):
        return None
    doubled = a + a
    L = len(a)
    for k in range(L):
        if doubled[k:k+L] == b:
            return k
    return None

# -------------------------
# Extraktion aus TTL
# -------------------------
def extract_declarations(ttl_text):
    """
    Liefert:
      row_forms: set of form IRIs (as 'mhg:...') found as 'a mhg:rowForm' or in hasRowForm lists
      row_classes: set of class IRIs found as 'a mhg:rowClass'
      map_rowform_to_rowclass: best-effort dict mapping 'mhg:form' -> 'mhg:rowClass' (if determinable)
    """
    row_forms = set()
    row_classes = set()
    rowform_to_rowclass = dict()

    # 1) find all declarations "mhg:... a mhg:rowForm" and "mhg:... a mhg:rowClass"
    for m in re.finditer(r"(mhg:\d+(?:_\d+)*)\s+a\s+mhg:rowForm\b", ttl_text):
        row_forms.add(m.group(1))
    for m in re.finditer(r"(mhg:\d+(?:_\d+)*)\s+a\s+mhg:rowClass\b", ttl_text):
        row_classes.add(m.group(1))

    # 2) find explicit hasRowClass on a rowForm statement block:
    #    look for patterns like: mhg:<form> ... mhg:hasRowClass mhg:<rowclass> ;
    stmt_pattern = re.compile(r"(mhg:\d+(?:_\d+)*)\s+([^.]*)\.")
    for m in stmt_pattern.finditer(ttl_text):
        subj = m.group(1)
        body = m.group(2)
        # if subject is a rowForm
        if re.search(r"\ba\s+mhg:rowForm\b", body) or subj in row_forms:
            # search for hasRowClass mhg:...
            hr = re.search(r"mhg:hasRowClass\s+(mhg:\d+(?:_\d+)*)", body)
            if hr:
                row_forms.add(subj)
                rowform_to_rowclass[subj] = hr.group(1)
        # if subject is a rowClass, and it has a hasRowForm list, extract forms
        if re.search(r"\ba\s+mhg:rowClass\b", body) or subj in row_classes:
            # find hasRowForm ... up to '.' in the block body (commas allowed)
            hrfs = re.findall(r"mhg:hasRowForm\s*(.*?)$", body, flags=re.M)
            # hrfs likely empty since body doesn't include following lines; handle differently below

    # 3) find rowClass blocks with hasRowForm lists across multiple lines
    # pattern: mhg:<rowclass> a mhg:rowClass ; ... mhg:hasRowForm <stuff> .
    block_pattern = re.compile(r"(mhg:\d+(?:_\d+)*)\s+a\s+mhg:rowClass\s*;(.*?)(?=\n\S|$)", re.S)
    # The above finds each rowClass header + following block lines (until next top-level subject or EOF)
    for m in block_pattern.finditer(ttl_text):
        rc = m.group(1)
        row_classes.add(rc)
        block = m.group(2)
        # find the hasRowForm clause within block (may extend across lines until a '.' that closes the triple)
        has_rf_match = re.search(r"mhg:hasRowForm\s*(.*?)(?:\n\s*\w|$)", block, re.S)
        # Better: search for "mhg:hasRowForm" and then capture until the next '.' in the overall text starting at this location:
        if "mhg:hasRowForm" in block:
            start = m.start(2) + block.index("mhg:hasRowForm")
            # find the next '.' after start in ttl_text
            dotpos = ttl_text.find(".", start)
            if dotpos != -1:
                clause = ttl_text[start:dotpos]
                # extract all mhg:... tokens from clause
                forms = re.findall(r"mhg:\d+(?:_\d+)*", clause)
                for f in forms:
                    row_forms.add(f)
                    # assign mapping f -> rc if not already mapped
                    if f not in rowform_to_rowclass:
                        rowform_to_rowclass[f] = rc

    # 4) also try to find inline triples where a rowForm subject declares hasRowClass (in one-liners)
    inline_pattern = re.compile(r"(mhg:\d+(?:_\d+)*)\s+([^.]*)\.")
    for m in inline_pattern.finditer(ttl_text):
        subj = m.group(1)
        body = m.group(2)
        if "mhg:hasRowClass" in body:
            rc_match = re.search(r"mhg:hasRowClass\s+(mhg:\d+(?:_\d+)*)", body)
            if rc_match:
                row_forms.add(subj)
                if subj not in rowform_to_rowclass:
                    rowform_to_rowclass[subj] = rc_match.group(1)

    # 5) fallback: any mhg:... token that looks like a rowForm candidate but not assigned, keep in row_forms set
    for m in IRI_RE.finditer(ttl_text):
        iri = "mhg:" + m.group(1)
        if iri not in row_forms and iri not in row_classes:
            # Heuristic: if its token length equals typical row length (has >=3 underscores), treat as rowForm candidate
            if m.group(1).count("_") >= 2:
                row_forms.add(iri)

    return row_forms, row_classes, rowform_to_rowclass

# -------------------------
# Build reverse mapping rowclass -> list of rowForms
# -------------------------
def build_class_to_forms(row_forms, row_classes, mapping):
    class_to_forms = defaultdict(list)
    for form in row_forms:
        cls = mapping.get(form)
        if cls is None:
            # attempt to find a class by searching nearby textual patterns not covered earlier is omitted
            continue
        class_to_forms[cls].append(form)
    return class_to_forms

# -------------------------
# Compare: find rotation pairs and group classes
# -------------------------
def find_rotation_relations(class_to_forms):
    # Build list of (form, class, vector)
    records = []
    for cls, forms in class_to_forms.items():
        for f in forms:
            vec = to_list_from_iri(f)
            if vec is None:
                continue
            records.append((f, cls, vec))

    # find pairs across different classes where one form is rotation of another
    pairs = []  # (formA, classA, formB, classB, shift)
    n = len(records)
    for i in range(n):
        fA, cA, vA = records[i]
        for j in range(i+1, n):
            fB, cB, vB = records[j]
            if cA == cB:
                continue
            if len(vA) != len(vB):
                continue
            shift = rotation_shift(vA, vB)
            if shift is not None:
                pairs.append((fA, cA, fB, cB, shift))
            else:
                # also check reverse (maybe vA is rotation of vB)
                shift2 = rotation_shift(vB, vA)
                if shift2 is not None:
                    pairs.append((fB, cB, fA, cA, shift2))

    # group classes by connectivity: if any pair links class X and Y they are in same group
    groups = []
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return parent.get(x, x)

    def union(a,b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # initialize parents
    for cls in class_to_forms.keys():
        parent[cls] = cls

    for _, cA, _, cB, _ in pairs:
        union(cA, cB)

    # collect groups
    tmp = defaultdict(list)
    for cls in parent.keys():
        tmp[find(cls)].append(cls)

    groups = list(tmp.values())
    return pairs, groups

# -------------------------
# Main
# -------------------------
def main():
    with open(INPUT_TTL, "r", encoding="utf-8") as f:
        text = f.read()

    row_forms, row_classes, mapping = extract_declarations(text)
    class_to_forms = build_class_to_forms(row_forms, row_classes, mapping)

    pairs, groups = find_rotation_relations(class_to_forms)

    # write pairs file
    with open(OUT_PAIRS, "w", encoding="utf-8") as pf:
        pf.write("formA\tclassA\tformB\tclassB\tshift\n")
        for fA,cA,fB,cB,shift in pairs:
            pf.write(f"{fA}\t{cA}\t{fB}\t{cB}\t{shift}\n")

    # write groups file (only groups with more than 1 class are interesting)
    with open(OUT_GROUPS, "w", encoding="utf-8") as gf:
        gf.write("Rotation groups of rowClasses (groups with >1 class):\n\n")
        for g in groups:
            if len(g) > 1:
                gf.write("Group:\n")
                for cls in g:
                    gf.write(f"  {cls}\n")
                gf.write("\n")

    print(f"Done. Pairs -> {OUT_PAIRS}, Groups -> {OUT_GROUPS}")
    if not pairs:
        print("No rotation pairs found. Check that rowForm->rowClass mappings were extracted correctly.")
    else:
        print(f"Found {len(pairs)} rotation pairs.")

if __name__ == "__main__":
    main()
