#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erzeugt eine TTL-Datei aus output.json:
Für jedes Intervallmuster mhg:xxx_yyy... wird ein Triple erzeugt:

mhg:xxx_yyy... a mhg:rowClass ;
    mhg:hasRowForm mhg:... , mhg:... , ... .

Alle 48 möglichen Reihenformen pro Werk werden aufgelistet.
"""

import json

# Prefixe für TTL-Datei
PREFIXES = """@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .
@prefix frbr: <http://purl.org/vocab/frbr/core/> .
@prefix schema: <https://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""

def write_rowclass_blocks(output_data, outfile):
    lines = [PREFIXES, "\n# --- Zwölfton-Reihen ---\n\n"]

    for work_key, info in output_data.items():
        if not isinstance(info, dict) or "SortedIntervalPatterns" not in info:
            continue

        # Alle 48 Reihenformen
        forms = info.get("All48Forms", [])
        if not forms:
            continue

        # 48 Reihenformen zu einer Zeile (durch Kommas getrennt)
        joined_forms = " ,\n        ".join(forms)

        # Für jedes Intervallmuster in SortedIntervalPatterns
        for pattern in info["SortedIntervalPatterns"]:
            block = f"{pattern} a mhg:rowClass ;\n" \
                    f"    mhg:hasRowForm {joined_forms} .\n\n"
            lines.append(block)

    # TTL schreiben
    with open(outfile, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ TTL-Datei erzeugt: {outfile}")

if __name__ == "__main__":
    with open("output.json", "r", encoding="utf-8") as f:
        output_data = json.load(f)

    write_rowclass_blocks(output_data, "rows.ttl")
