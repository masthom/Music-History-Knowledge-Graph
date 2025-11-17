import re

# ------------------------------------------------------------
# Einstellungen
# ------------------------------------------------------------

ttl_file = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"

# Regex: schema:name "Nachname, Vorname"
pattern = re.compile(
    r'schema:name\s+"([^"]+,\s*[^"]+)"',
    re.IGNORECASE
)

# ------------------------------------------------------------
# Datei einlesen
# ------------------------------------------------------------

with open(ttl_file, "r", encoding="utf-8") as f:
    ttl_data = f.read()

# ------------------------------------------------------------
# Namen extrahieren
# ------------------------------------------------------------

raw_names = pattern.findall(ttl_data)

# ------------------------------------------------------------
# Namen konvertieren: "Nachname, Vorname" → "Vorname Nachname"
# ------------------------------------------------------------

converted = []
for full in raw_names:
    if "," in full:
        last, first = full.split(",", 1)
        first = first.strip()
        last = last.strip()
        converted.append(f"{first} {last}")
    else:
        converted.append(full)

# Duplikate entfernen + sortieren (optional)
converted = sorted(set(converted))

# ------------------------------------------------------------
# SPARQL-VALUES-Liste erzeugen
# ------------------------------------------------------------

print("VALUES ?searchName {")
for name in converted:
    print(f'  "{name}"')
print("}")
