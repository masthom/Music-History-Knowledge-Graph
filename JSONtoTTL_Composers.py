#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erstellt eine TTL-Datei mit Komponistenblöcken aus output.json.
- Keine Initialen am Anfang der Work-IRIs (Nachname statt Initialen)
- Alle Werke eines Komponisten unter einem gemeinsamen Block
"""

import json
import re
from pathlib import Path

INPUT = Path("output.json")
OUTPUT = Path("Composers_updated_with_multiple_works_noInitials.ttl")

PREFIXES = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix frbr: <http://purl.org/vocab/frbr/core/> .
@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .
@prefix schema: <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# --- Ergänzte Komponisten ---


"""

def normalize_name(name):
    """Gibt (first, last, safe_full) für einen Komponisten zurück."""
    if "," in name:
        last, first = [n.strip() for n in name.split(",", 1)]
    else:
        parts = name.strip().split()
        first, last = parts[0], parts[-1]
    safe_full = re.sub(r"[^A-Za-z0-9]", "", first + last)
    return first, last, safe_full

def short_work_title(work):
    """Z. B. 'Fischerhaus-Serenade, Op.45' → 'FischerhausSerenade_Op45'"""
    return re.sub(r'[^A-Za-z0-9]+', '_', work).strip('_')

# === JSON laden ===
with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

# Komponisten und Werke sammeln
composer_data = {}

for key, entry in data.items():
    if not isinstance(entry, dict):
        continue
    composer = entry.get("Composer")
    work = entry.get("Work")
    if not composer or not work:
        continue
    first, last, safe = normalize_name(composer)
    work_title = short_work_title(work)
    work_iri = f"mhg:{last}_{work_title}"
    comp_key = composer.strip()
    composer_data.setdefault(comp_key, {
        "first": first,
        "last": last,
        "safe": safe,
        "works": set()
    })
    composer_data[comp_key]["works"].add(work_iri)

# === TTL-Ausgabe erzeugen ===
lines = [PREFIXES]

for comp, info in sorted(composer_data.items()):
    full_iri = f"mhg:{info['first']}{info['last']}"
    works_str = " ,\n        ".join(sorted(info["works"]))
    
    block = f"""{full_iri} a mhg:composer ;
    frbr:creatorOf {works_str} ;
    schema:name "{comp}" ;
    # schema:birthDate "YYYY-MM-DD" ;
    # schema:deathDate "YYYY-MM-DD" ;
    # schema:birthPlace "..." ;
    # schema:sameAs <...> .

"""
    lines.append(block)

# === Datei schreiben ===
OUTPUT.write_text("".join(lines), encoding="utf-8")

print(f"✅ Datei erzeugt: {OUTPUT}")
print(f"→ {len(composer_data)} Komponistenblöcke erstellt.")
