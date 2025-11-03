#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt RDF/Turtle für RowClasses und RowForms auf Basis von output.json.
Nur das lexikographisch kleinste Pattern wird als RowClass deklariert.
"""

import json
import re
from pathlib import Path

INPUT = Path("output.json")
OUTPUT = Path("rows_rowclasses4.ttl")

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

# ----------------------------------------------------------------------

def process_entry(entry):
    work = entry.get("Work", "")
    work_local = sanitize_local(work, "w")

    sorted_patterns = entry.get("SortedIntervalPatterns", [])
    if not sorted_patterns:
        return None

    # Nur lexikographisch kleinstes Pattern
    smallest = sorted(sorted_patterns)[0]
    all_forms = entry.get("All48Forms", [])
    original_p = entry.get("OriginalP", "")
    source = entry.get("Source", "")

    lines = []
    lines.append("## Intervallmuster:")
    for label, pattern in zip(("P", "I", "R", "RI"), sorted_patterns):
        lines.append(f"## {label}: {pattern.replace('mhg:', '')}")
    lines.append("")

    # --- RowClass-Block ---
    lines.append(f"{smallest} a mhg:RowClass ;")
    lines.append(f"    mhg:actualizedIn mhg:{work_local} ;")
    lines.append(f"    mhg:hasRowForm")

    # alle 48 Formen auflisten
    grouped = {"P": all_forms[0:12], "I": all_forms[12:24],
               "R": all_forms[24:36], "RI": all_forms[36:48]}

    # Jede Gruppe einzeln mit Kommentar
    for label, forms in grouped.items():
        if not forms:
            continue
        lines.append(f"        # {label}-Formen")
        for i, form in enumerate(forms):
            sep = " ," if i < len(forms) - 1 else " ,"
            lines.append(f"        {form}{sep}")
    lines[-1] = lines[-1][:-2] + " .\n"  # letztes Komma durch Punkt ersetzen

    # --- RowForm-Tripel ---
    lines.append("# --- Einzelne RowForms ---")
    for label, forms in grouped.items():
        if not forms:
            continue
        lines.append(f"# {label}-FORMS")
        for form in forms:
            lines.append(f"{form} mhg:hasRowClass {smallest} .")
            if form == original_p:
                # nur für Original-P-Form manifestedIn hinzufügen
                lines.append(f"{form} mhg:manifestedIn [")
                lines.append('    mhg:accordingTo "SerialAnalyzer" ;')
                if source:
                    lines.append(f'    dcterms:source "{lit(source)}" ;')
                lines.append(f"    mhg:manifestedIn mhg:{work_local} ] .")
        lines.append("")
    return "\n".join(lines)

# ----------------------------------------------------------------------

def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    out_lines = [PREFIXES]

    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        block = process_entry(entry)
        if block:
            out_lines.append(block)
            out_lines.append("")

    OUTPUT.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"✅ TTL-Datei erzeugt: {OUTPUT}")

if __name__ == "__main__":
    main()
