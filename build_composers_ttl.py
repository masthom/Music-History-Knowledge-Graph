import json, re, os
from datetime import date

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
for key, entry in data.items():
    comp = entry["Composer"]
    work = entry["Work"]
    composer_works.setdefault(comp, []).append(work)

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

    block = f"""mhg:{safe} a mhg:composer ;
    frbr:creatorOf {creators} ;
    schema:name "{composer}" ;
    # schema:birthDate "YYYY-MM-DD" ;
    # schema:deathDate "YYYY-MM-DD" ;
    # schema:birthPlace "..." ;
    # schema:sameAs <...> .

"""
    out_lines.append(block)

# === Datei schreiben ===
out_file = "Composers_updated_with_multiple_works.ttl"
with open(out_file, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print(f"✅ Datei erzeugt: {out_file} ({len(composer_works)} Komponisten)")
