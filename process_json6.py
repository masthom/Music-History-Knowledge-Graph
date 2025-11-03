#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt RDF/Turtle mit Deduplikation:
- Jede RowClass nur einmal (lexikographisch kleinste Reihe)
- Jede RowForm verweist auf ihre RowClass
- Nur die RowForm == "OriginalP" erhält mhg:manifestedIn
"""

import json, re
from pathlib import Path
from collections import defaultdict

INPUT = Path("output.json")
OUTPUT = Path("rows_rowclasses6.ttl")

PREFIXES = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix frbr: <http://purl.org/vocab/frbr/core/> .
@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

def sanitize_local(s, prefix="w"):
    if not s:
        return None
    s = str(s).strip().strip('"')
    s = re.sub(r"[^\w\d]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return None
    if re.match(r"^\d", s):
        s = "_" + s
    return f"{prefix}_{s}"

def lit(s):
    return str(s).replace('"', '\\"') if s else None

# --- Daten einlesen ---
with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

rowclasses = {}
rowforms = defaultdict(lambda: {"rowclass": None, "works": set(), "sources": set(), "is_original": False})

for key, entry in data.items():
    if not isinstance(entry, dict):
        continue

    composer = entry.get("Composer", "")
    composer_clean = re.sub(r"[,;].*$", "", composer).strip()
    work = entry.get("Work", "")
    work_local = sanitize_local(f"{composer_clean}_{work}", "w")

    sorted_patterns = entry.get("SortedIntervalPatterns", [])
    if not sorted_patterns:
        continue

    # kleinste Form lexikographisch bestimmen
    def pattern_key(p): return tuple(map(int, p.replace("mhg:", "").split("_")))
    smallest = sorted(sorted_patterns, key=pattern_key)[0]

    all_forms = entry.get("All48Forms", [])
    grouped = {"P": all_forms[0:12], "I": all_forms[12:24],
               "R": all_forms[24:36], "RI": all_forms[36:48]}

    # RowClass speichern
    rc_entry = rowclasses.setdefault(
        smallest, {"works": set(), "grouped": grouped, "patterns": sorted_patterns}
    )
    rc_entry["works"].add(work_local)

    # RowForms registrieren
    original_p = entry.get("OriginalP")
    for label, forms in grouped.items():
        for form in forms:
            rowforms[form]["rowclass"] = smallest
            if form == original_p:
                # Nur diese Form markiert als original
                rowforms[form]["is_original"] = True
                rowforms[form]["works"].add(work_local)
                if entry.get("Source"):
                    rowforms[form]["sources"].add(entry["Source"])

# --- TTL schreiben ---
lines = [PREFIXES, "# --- RowClasses (dedupliziert) ---\n"]

for rc, info in sorted(rowclasses.items(), key=lambda x: x[0]):
    lines.append("## Intervallmuster:")
    for label, pattern in zip(("P", "I", "R", "RI"), info["patterns"]):
        lines.append(f"## {label}: {pattern.replace('mhg:', '')}")
    lines.append("")

    works_str = " ,\n        ".join(f"mhg:{w}" for w in sorted(info["works"]))

    lines.append(f"{rc} a mhg:RowClass ;")
    lines.append(f"    mhg:actualizedIn {works_str} ;")
    lines.append(f"    mhg:hasRowForm")

    for label in ("P", "I", "R", "RI"):
        forms = info["grouped"].get(label, [])
        if not forms:
            continue
        lines.append(f"        # {label}-Formen")
        for i, form in enumerate(forms):
            sep = " ," if i < len(forms) - 1 else " ,"
            lines.append(f"        {form}{sep}")
    lines[-1] = lines[-1][:-2] + " .\n"

lines.append("\n# --- RowForms ---\n")

for form, info in sorted(rowforms.items(), key=lambda x: x[0]):
    rc = info["rowclass"]
    lines.append(f"{form} mhg:hasRowClass {rc} .")
    if info["is_original"] and info["works"]:
        works_str = " ,\n            ".join(f"mhg:{w}" for w in sorted(info["works"]))
        lines.append(f"{form} mhg:manifestedIn [")
        lines.append('        mhg:accordingTo "SerialAnalyzer" ;')
        for src in sorted(info["sources"]):
            lines.append(f'        dcterms:source "{lit(src)}" ;')
        lines.append(f"        mhg:manifestedIn {works_str} ] .")
    lines.append("")

OUTPUT.write_text("\n".join(lines), encoding="utf-8")

num_rc = len(rowclasses)
num_rf = len(rowforms)
num_manifested = sum(1 for v in rowforms.values() if v["is_original"])
print(f"✅ TTL-Datei erzeugt: {OUTPUT}")
print(f"→ {num_rc} RowClasses, {num_rf} RowForms, davon {num_manifested} mit manifestedIn")
