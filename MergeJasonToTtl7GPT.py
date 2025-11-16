import json
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# === CONFIG ===========================================================
TTL_FILE = "composers_interim.ttl"
JSON_FILE = "query_Wikidata.json"
OUTPUT_TTL = "composers_updatedGPT.ttl"
LOG_FILE = "composers_updatedGPT_changes.log"

SCHEMA = Namespace("http://schema.org/")
MHG = Namespace("http://music-history-graph.ch/twelve-tone-onto#")  # ggf. anpassen
# =====================================================================

import re

def normalize_name(label):
    label = label.strip()
    label = label.replace("(", "").replace(")", "")
    label = re.sub(r"\s+", " ", label)

    if "," in label:
        last, first = label.split(",", 1)
        last, first = last.strip(), first.strip()
    else:
        parts = label.split(" ")
        last = parts[-1]
        first = " ".join(parts[:-1])

    first = first.split(" ")[0]

    return f"{last.lower()}_{first.lower()}"


def main():
    # --- Lade TTL ---
    g = Graph()
    g.parse(TTL_FILE, format="turtle")

    # --- Lade JSON ---
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        persons = json.load(f)

    change_log = []

    # --- Baue Lookup: normalisierte Namen → JSON-Datensatz ---
    json_index = {}
    for p in persons:
        normalized = normalize_name(p["personLabel"])
        json_index[normalized] = p

    # Debug: verfügbare JSON-Namen
    print("JSON Normalized Names:")
    for k in json_index.keys():
        print("  ", k)

    # --- Verarbeite jeden Eintrag aus dem TTL ---
    for s, _, name_literal in g.triples((None, SCHEMA.name, None)):
        ttl_label_raw = str(name_literal)
        ttl_norm = normalize_name(ttl_label_raw)

        print(f"TTL name '{ttl_label_raw}' → {ttl_norm}")

        if ttl_norm not in json_index:
            print(f"  ❌ Not found in JSON: {ttl_norm}")
            continue
        else:
            print(f"  ✔ Match: {ttl_norm}")

        item = json_index[ttl_norm]

        qid_uri = URIRef(item["person"])
        json_birth = item.get("birthDate")
        json_birthplace = item.get("birthPlace")
        json_death = item.get("deathDate")
        json_deathplace = item.get("deathPlace")

        # === SAMEAS ===
        ttl_same = set(o for _, _, o in g.triples((s, SCHEMA.sameAs, None)))
        if qid_uri not in ttl_same:
            g.add((s, SCHEMA.sameAs, qid_uri))
            change_log.append(f"{s}: added schema:sameAs {qid_uri}")

        # === BIRTH DATE ===
        if json_birth:
            ttl_birth = next((str(o) for _, _, o in g.triples((s, SCHEMA.birthDate, None))), None)
            if ttl_birth != json_birth[:10]:
                if ttl_birth:
                    g.remove((s, SCHEMA.birthDate, None))
                    change_log.append(f"{s}: corrected birthDate {ttl_birth} → {json_birth[:10]}")
                g.add((s, SCHEMA.birthDate, Literal(json_birth[:10], datatype=XSD.date)))

        # === BIRTH PLACE ===
        if json_birthplace:
            ttl_bp = next((o for _, _, o in g.triples((s, SCHEMA.birthPlace, None))), None)
            bp_uri = URIRef(json_birthplace)
            if ttl_bp != bp_uri:
                if ttl_bp:
                    g.remove((s, SCHEMA.birthPlace, ttl_bp))
                    change_log.append(f"{s}: corrected birthPlace {ttl_bp} → {bp_uri}")
                g.add((s, SCHEMA.birthPlace, bp_uri))

        # === DEATH DATE ===
        if json_death:
            ttl_death = next((str(o) for _, _, o in g.triples((s, SCHEMA.deathDate, None))), None)
            if ttl_death != json_death[:10]:
                if ttl_death:
                    g.remove((s, SCHEMA.deathDate, None))
                    change_log.append(f"{s}: corrected deathDate {ttl_death} → {json_death[:10]}")
                g.add((s, SCHEMA.deathDate, Literal(json_death[:10], datatype=XSD.date)))

        # === DEATH PLACE ===
        if json_deathplace:
            ttl_dp = next((o for _, _, o in g.triples((s, SCHEMA.deathPlace, None))), None)
            dp_uri = URIRef(json_deathplace)
            if ttl_dp != dp_uri:
                if ttl_dp:
                    g.remove((s, SCHEMA.deathPlace, ttl_dp))
                    change_log.append(f"{s}: corrected deathPlace {ttl_dp} → {dp_uri}")
                g.add((s, SCHEMA.deathPlace, dp_uri))

    # --- Ausgabe ---
    g.serialize(OUTPUT_TTL, format="turtle")
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(change_log))

    print("Fertig! Änderungen protokolliert.")


if __name__ == "__main__":
    main()
