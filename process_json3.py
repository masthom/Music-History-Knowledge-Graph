#!/usr/bin/env python3
import json
import re
from pathlib import Path

INPUT = Path("output.json")
OUTPUT = Path("rows_and_rowclasses.ttl")

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
    s = re.sub(r'[^\w\d]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    if not s:
        return None
    if re.match(r'^\d', s):
        s = "_" + s
    return f"{prefix}_{s}"

def lit(s):
    return str(s).replace('"', '\\"') if s is not None else None

# -------------------------------------------------------------------------
data = json.loads(INPUT.read_text(encoding="utf-8"))

out = [PREFIXES]
declared_rowclasses = set()

for key, entry in data.items():
    if not isinstance(entry, dict):
        continue

    work_label = entry.get("Work") or ""
    composer_label = entry.get("Composer") or ""
    year = entry.get("Year") or ""
    source = entry.get("Source") or ""
    sip = entry.get("SortedIntervalPatterns") or []
    all_forms = entry.get("All48Forms") or []
    originalp = entry.get("OriginalP") or ""

    # Werk-IRI
    if not work_label:
        if "_-_" in key:
            work_label = key.split("_-_", 1)[1]
        else:
            work_label = key
    work_local = sanitize_local(work_label, prefix="w")

    # --- 1. RowClass-Tripel (Doubletten vermeiden) ---
    for pattern in sip:
        if not pattern or not pattern.startswith("mhg:"):
            continue
        if pattern not in declared_rowclasses:
            declared_rowclasses.add(pattern)
            out.append(f"{pattern} a mhg:RowClass ;")
            # alle 48 Formen
            if all_forms:
                joined = " ,\n        ".join(all_forms)
                out.append(f"    mhg:hasRowForm {joined} .\n")
            else:
                out.append("    # keine Formen gefunden .\n")
        else:
            # falls schon vorhanden: kein neuer Block, aber Kommentar
            out.append(f"# {pattern} bereits definiert, Verweis auf mhg:{work_local}\n")

    # --- 2. P0-Formen: mhg:manifestedIn-Block ---
    if isinstance(all_forms, list):
        for f in all_forms:
            # wir nehmen an, dass der erste Eintrag der P0 entspricht
            if all_forms.index(f) == 0:
                out.append(f"{f} mhg:manifestedIn [")
                out.append('        mhg:accordingTo "SerialAnalyzer" ;')
                if source:
                    out.append(f'        dcterms:source "{lit(source)}" ;')
                out.append(f"        mhg:manifestedIn mhg:{work_local} ] .\n")

    out.append("")

# -------------------------------------------------------------------------
OUTPUT.write_text("\n".join(out), encoding="utf-8")
print(f"✅ TTL-Datei erzeugt: {OUTPUT}")
print(f"Enthaltene RowClasses: {len(declared_rowclasses)}")
