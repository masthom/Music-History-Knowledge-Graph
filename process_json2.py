#!/usr/bin/env python3
import json
import re
from pathlib import Path

INPUT = Path("output.json")
OUTPUT = Path("output_from_json.ttl")

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
    s = str(s).strip()
    # remove surrounding quotes if present
    s = s.strip('"').strip()
    # replace sequences of non-alphanum with underscore
    s = re.sub(r'[^\w\d]+', '_', s, flags=re.UNICODE)
    s = re.sub(r'_+', '_', s).strip('_')
    if not s:
        return None
    if re.match(r'^\d', s):
        s = "_" + s
    return f"{prefix}_{s}"

def lit(s):
    return str(s).replace('"', '\\"') if s is not None else None

data = json.loads(INPUT.read_text(encoding="utf-8"))

out = [PREFIXES]
declared_composers = set()

for key, entry in data.items():
    if isinstance(entry, dict):
        work_label = entry.get("Work") or ""
        composer_label = entry.get("Composer") or ""
        year = entry.get("Year") or ""
        source = entry.get("Source") or ""
        sip = entry.get("SortedIntervalPatterns") or []
    else:
        work_label = ""
        composer_label = ""
        year = ""
        source = ""
        sip = []

    # fallback: if Work missing, derive from key after "_-_"
    if not work_label:
        if "_-_" in key:
            work_label = key.split("_-_", 1)[1]
        else:
            work_label = key

    if not composer_label:
        if "_-_" in key:
            composer_label = key.split("_-_", 1)[0].replace("_", " ")
        else:
            composer_label = ""

    work_local = sanitize_local(work_label, prefix="w") or sanitize_local(key, prefix="w")
    composer_local = sanitize_local(composer_label, prefix="c") if composer_label else None

    # Work triples
    out.append(f"# {key}")
    out.append(f"mhg:{work_local} a mhg:composition, frbr:work ;")
    if composer_local:
        out.append(f"    frbr:creator mhg:{composer_local} ;")
    if year:
        out.append(f'    frbr:hasCreationDate "{lit(year)}" .')
    else:
        # close triple if no year
        if composer_local:
            # replace trailing ';' with '.'
            out[-1] = out[-1].rstrip(' ;') + " ."
        else:
            out[-1] = out[-1].rstrip(' ;') + " ."

    # SortedIntervalPatterns: take first non-empty string
    pattern = None
    if isinstance(sip, list):
        for it in sip:
            if isinstance(it, str) and it.strip():
                pattern = it.strip()
                break

    if pattern:
        # use as-is if already has prefix ':', else sanitize
        if ":" in pattern:
            subj = pattern
        else:
            subj = "mhg:" + re.sub(r'[^\w\d]+', '_', pattern).strip('_')
        out.append(f"{subj} a mhg:RowClass ;")
        out.append("    mhg:actualizedIn [")
        out.append('        mhg:accordingTo "SerialAnalyzer" ;')
        if source:
            out.append(f'        dcterms:source "{lit(source)}" ;')
        out.append(f"        mhg:actualizedIn mhg:{work_local} ] .")

    out.append("")  # blank line

OUTPUT.write_text("\n".join(out), encoding="utf-8")
print(f"Wrote {OUTPUT}")