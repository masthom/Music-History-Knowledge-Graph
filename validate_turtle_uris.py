import re
from pathlib import Path

ttl_file = Path("MusicHistoryGraph_TwelveToneMusic_NORMALIZED_SAFE.ttl")

# Regex zum Extrahieren von URIs nach mhg:, frbr:, schema: usw.
uri_pattern = re.compile(r"\b([a-zA-Z0-9_-]+:[A-Za-z0-9_~.\-\(\)\+\#]*)\b")

invalid = []
allowed_prefixes = {
    "mhg", "frbr", "schema", "owl", "rdf", "rdfs",
    "xsd", "dc", "dcterms", "wd"
}

for i, line in enumerate(ttl_file.read_text(encoding="utf-8").splitlines(), start=1):
    for uri in uri_pattern.findall(line):
        prefix = uri.split(":")[0]
        if prefix not in allowed_prefixes:
            continue
        local = uri.split(":", 1)[1]
        # prüfe unzulässige Zeichen
        if re.search(r"[^A-Za-z0-9_~.\-]", local):
            invalid.append((i, uri))

print(f"🔎 {len(invalid)} potenziell ungültige URIs gefunden.\n")
for i, uri in invalid[:40]:
    print(f"Zeile {i}: {uri}")
if len(invalid) > 40:
    print(f"... und {len(invalid)-40} weitere.")
