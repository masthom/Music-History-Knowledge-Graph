import json, re, os, time
from datetime import date

import requests
from urllib.parse import quote

def get_birth_death_from_wikidata(name):
    """
    Versucht, für einen gegebenen Komponistennamen aus Wikidata
    schema:birthDate und schema:deathDate zu ermitteln.
    Gibt (birth, death) zurück oder (None, None).
    """
    query = f"""
    SELECT ?birth ?death WHERE {{
      ?person rdfs:label "{name}"@en .
      OPTIONAL {{ ?person wdt:P569 ?birth . }}
      OPTIONAL {{ ?person wdt:P570 ?death . }}
    }} LIMIT 1
    """
    url = "https://query.wikidata.org/sparql"
    headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "MusicHistoryGraphBot/1.0 (contact: https://github.com/masthom/Music-History-Knowledge-Graph)"
}

    params = {"query": query}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", {}).get("bindings", [])
        if results:
            birth = results[0].get("birth", {}).get("value")
            death = results[0].get("death", {}).get("value")
            # nur YYYY-MM-DD extrahieren
            if birth:
                birth = birth.split("T")[0]
            if death:
                death = death.split("T")[0]
            return birth, death
                
    except Exception as e:
        print(f"Wikidata-Abfrage für {name} fehlgeschlagen: {e}")
    return None, None
# ... nach return birth, death oder am Ende der try/except: 
time.sleep(1.5)


def normalize_name(name):
    # "Berg, Alban" -> ("Alban", "Berg", "AB", "AlbanBerg")
    if "," in name:
        last, first = [n.strip() for n in name.split(",", 1)]
    else:
        parts = name.split()
        first, last = parts[0], parts[-1]
    initials = (first[0] + last[0]).upper()
    safe = re.sub(r'[^A-Za-z0-9]', '', first + last)
    return first, last, initials, safe

def short_work_title(work):
    # "Fischerhaus-Serenade, Op.45" → "FischerhausSerenade_Op45"
    w = re.sub(r'[^A-Za-z0-9]+', '_', work).strip('_')
    return w

def build_creator_line(initials, works):
    return ",\n                   ".join(
        [f"mhg:{initials}_{short_work_title(w)}" for w in works]
    )

# === Datei laden ===
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Alle Komponisten und ihre Werke sammeln
composer_works = {}

composer_works = {}

for key, entry in data.items():
    # Nur echte Werk-Einträge: Sie müssen Dicts mit "Composer" UND "Work" enthalten
    if isinstance(entry, dict) and "Composer" in entry and "Work" in entry:
        composer = entry["Composer"].strip()
        work = entry["Work"].strip()
        composer_works.setdefault(composer, []).append(work)
    else:
        # Debug-Ausgabe: zeigt dir, was übersprungen wird
        print(f"⚠️  Übersprungen: {key}")

    #comp = entry["Composer"].strip()
    #work = entry["Work"].strip()
    #composer_works.setdefault(comp, []).append(work)


# Bestehende TTL-Datei laden (für Prefixe etc.)
with open("Composers.ttl", "r", encoding="utf-8") as f:
    ttl_prefix = []
    for line in f:
        ttl_prefix.append(line)
        if not line.strip().startswith("@prefix"):
            break
    ttl_header = "".join(ttl_prefix)

# === Ausgabe vorbereiten ===
out_lines = [ttl_header, "\n# --- Ergänzte Komponisten ---\n\n"]

for composer, works in sorted(composer_works.items()):
    first, last, initials, safe = normalize_name(composer)
    creators = build_creator_line(initials, works)

    birth, death = get_birth_death_from_wikidata(composer)

    if birth:
        birth_line = f'schema:birthDate "{birth}" ;'
    else:
        birth_line = '# schema:birthDate "YYYY-MM-DD" ;'

    if death:
        death_line = f'schema:deathDate "{death}" ;'
    else:
        death_line = '# schema:deathDate "YYYY-MM-DD" ;'

    block = f"""mhg:{safe} a mhg:composer ;
        frbr:creatorOf {creators} ;
        schema:name "{composer}" ;
        {birth_line}
        {death_line}
        # schema:birthPlace "..." ;
        # schema:sameAs <...> .

    """
    out_lines.append(block)

for i, (composer, works) in enumerate(sorted(composer_works.items()), 1):
    print(f"[{i}/{len(composer_works)}] {composer} ...")
    ...

print("Anzahl erzeugter Komponistenblöcke:", len(out_lines))

# === Datei schreiben ===
# === Datei schreiben ===
out_file = "Composers_updated_with_multiple_works.ttl"
with open(out_file, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print(f"✅ Datei erzeugt: {out_file} ({len(composer_works)} Komponisten)")
print("Beispielauszug:\n", "".join(out_lines[:5]))




