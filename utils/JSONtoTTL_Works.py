#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erstellt eine TTL-Datei mit allen Werken aus output.json.
Kompatibel zur Komponisten-Datei: Komponisten-IRIs im Format mhg:VornameNachname

Beispielausgabe:

mhg:Krenek_Lamentatio_Jeremiae_Prophetae_Op93_row_6 a mhg:composition , frbr:work ;
    frbr:creator mhg:ErnstKrenek ;
    frbr:hasCreationDate "1941" .
"""

import json
import re
from pathlib import Path

INPUT = Path("output.json")
OUTPUT = Path("Works_from_output_v2.ttl")

PREFIXES = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix frbr: <http://purl.org/vocab/frbr/core/> .
@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .
@prefix schema: <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# --- Ergänzte Werke ---


"""

def normalize_name(name: str):
    """
    Extrahiert Nachname und Vorname und liefert (first, last, safe_full).
    Beispiel: "Krenek, Ernst" → ("Ernst", "Krenek", "ErnstKrenek")
    """
    if "," in name:
        last, first = [n.strip() for n in name.split(",", 1)]
    else:
        parts = name.strip().split()
        first, last = parts[0], parts[-1]
    safe_full = re.sub(r'[^A-Za-z0-9]', '', first + last)
    return first, last, safe_full

def short_work_title(work: str):
    """ 'Lamentatio Jeremiae Prophetae, Op.93 (row 6)' → 'Lamentatio_Jeremiae_Prophetae_Op93_row_6' """
    return re.sub(r'[^A-Za-z0-9]+', '_', work).strip('_')

# === JSON laden ===
with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

lines = [PREFIXES]
seen_works = set()

for key, entry in data.items():
    if not isinstance(entry, dict):
        continue
    composer = entry.get("Composer")
    work = entry.get("Work")
    year = entry.get("Year", "")
    if not composer or not work:
        continue

    # Komponist-IRI im Stil mhg:VornameNachname
    first, last, safe_full = normalize_name(composer)
    composer_iri = f"mhg:{safe_full}"

    # Werk-IRI im Stil mhg:Nachname_<Werk>
    work_iri = f"mhg:{last}_{short_work_title(work)}"
    if work_iri in seen_works:
        continue
    seen_works.add(work_iri)

    # TTL-Block
    block = f"""{work_iri} a mhg:composition , frbr:work ;
    frbr:creator {composer_iri} ;
    frbr:hasCreationDate "{year}" .

"""
    lines.append(block)

# === Datei schreiben ===
OUTPUT.write_text("".join(lines), encoding="utf-8")

print(f"✅ Datei erzeugt: {OUTPUT}")
print(f"→ {len(seen_works)} Werke exportiert.")
