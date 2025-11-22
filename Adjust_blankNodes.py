#!/usr/bin/env python3
# coding: utf-8
"""
Robustes Transformationsskript für mhg:manifestedIn [ ... ] -Blöcke.
Kernanforderungen:
 - sammle alle mhg:manifestedIn-Objekte (egal wo im Block)
 - erzeuge äußere Liste mit ihnen und ein inneres [ mhg:manifestedIn ... ; ... ]-Block
 - respektiere Kommata innerhalb von Anführungszeichen (z.B. dcterms:source "Arnold, p.1")
 - setze Semikola/Kommas korrekt, letzter Eintrag vor ']' ohne Semikolon
"""

import re
from typing import List, Tuple

INPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_CompleteAdjust.ttl"

# regex: find whole "mhg:manifestedIn [ ... ] ." blocks (DOTALL)
BLOCK_RE = re.compile(r"mhg:manifestedIn\s*\[\s*(.*?)\s*\]\s*\.", re.DOTALL)

# split statements by semicolon (keep quoted semicolons if any — rare), then strip
def split_statements(block: str) -> List[str]:
    parts = [p.strip() for p in re.split(r";\s*", block)]
    return [p for p in parts if p]

# split on commas that are NOT inside double quotes
_COMMA_OUTSIDE_QUOTES_RE = re.compile(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)')

def split_objects(objstr: str) -> List[str]:
    """Split object list by commas excluding commas inside quotes, and trim whitespace."""
    items = [it.strip() for it in _COMMA_OUTSIDE_QUOTES_RE.split(objstr) if it.strip()]
    return items

# parse a statement into (predicate_or_None, [obj,...])
def parse_statement(stmt: str) -> Tuple[str, List[str]]:
    s = stmt.strip()
    if not s:
        return (None, [])
    # If there's a predicate token (has colon before first whitespace)
    m = re.match(r'^([^\s]+)\s+(.*)$', s, re.DOTALL)
    if not m:
        # treat as continuation objects
        objs = split_objects(s)
        return (None, objs)
    pred_candidate = m.group(1)
    rest = m.group(2).strip()
    # If pred_candidate contains ':', treat as predicate
    if ':' in pred_candidate:
        # remove trailing ] or . if present
        rest = rest.rstrip(' .]')
        objs = split_objects(rest)
        return (pred_candidate, objs)
    else:
        # no predicate — treat entire statement as objects
        objs = split_objects(s)
        return (None, objs)

def extract_manifests_and_fields(block: str) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
    stmts = split_statements(block)
    manifests: List[str] = []
    fields: List[Tuple[str, List[str]]] = []
    last_pred = None

    for stmt in stmts:
        pred, objs = parse_statement(stmt)
        if pred is None:
            # continuation line: attach to last_pred if any
            if last_pred is None:
                # fallback to manifests
                for o in objs:
                    if o not in manifests:
                        manifests.append(o)
            else:
                if last_pred == "mhg:manifestedIn":
                    for o in objs:
                        if o not in manifests:
                            manifests.append(o)
                else:
                    # append to last field
                    if fields and fields[-1][0] == last_pred:
                        for o in objs:
                            if o not in fields[-1][1]:
                                fields[-1][1].append(o)
                    else:
                        fields.append((last_pred, objs.copy()))
            continue

        # pred exists
        last_pred = pred
        if pred == "mhg:manifestedIn":
            for o in objs:
                if o not in manifests:
                    manifests.append(o)
        else:
            fields.append((pred, objs.copy()))

    return manifests, fields

def build_replacement(manifests: List[str], fields: List[Tuple[str, List[str]]]) -> str:
    indent_outer = "        "
    indent_inner = "            "
    indent_block = "    "

    lines: List[str] = []

    # Outer list
    if manifests:
        outer_text = indent_outer + "mhg:manifestedIn " + (",\n" + indent_outer).join(manifests) + " ,"
        lines.append(outer_text)

    # Inner block start: immediate manifestedIn list
    if manifests:
        inner_first = indent_block + "[ mhg:manifestedIn " + (",\n" + indent_inner).join(manifests) + " ;"
    else:
        inner_first = indent_block + "["
    lines.append(inner_first)

    # Fields: each field printed as pred obj1 , obj2 ; except last field ends with ' ] .'
    if fields:
        for idx, (pred, objs) in enumerate(fields):
            obj_text = (",\n" + indent_inner).join(objs)
            if idx < len(fields) - 1:
                lines.append(f"{indent_inner}{pred} {obj_text} ;")
            else:
                # last field: close inner block
                lines.append(f"{indent_inner}{pred} {obj_text} ] .")
    else:
        # no additional fields: close block after manifestedIn list
        # replace trailing semicolon in inner_first with closing
        if lines and lines[-1].endswith(" ;"):
            lines[-1] = lines[-1][:-2] + " ] ."
        else:
            lines.append(indent_block + "] .")

    return "\n".join(lines)

def transform_file(infile: str, outfile: str):
    text = open(infile, "r", encoding="utf-8").read()

    def repl(m: re.Match) -> str:
        inner = m.group(1)
        manifests, fields = extract_manifests_and_fields(inner)
        newblock = build_replacement(manifests, fields)
        return newblock

    new_text = BLOCK_RE.sub(repl, text)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"Wrote transformed TTL to: {outfile}")

if __name__ == "__main__":
    transform_file(INPUT_FILE, OUTPUT_FILE)
