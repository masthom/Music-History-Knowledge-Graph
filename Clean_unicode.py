# -*- coding: utf-8 -*-
# Entfernt unsichtbare/ungültige Zeichen aus einer Turtle-Datei

input_file = "MusicHistoryGraph_TwelveToneMusic_TEST.ttl"
output_file = "MusicHistoryGraph_TwelveToneMusic_TEST_clean.ttl"

with open(input_file, "rb") as f:
    content = f.read()

# Suche nach verdächtigen Zeichen
suspicious = {
    b"\xef\xbb\xbf": "BOM (Byte Order Mark)",
    b"\x00": "NULL-Byte",
    b"\xa0": "Non-breaking space (U+00A0)",
    b"\xe2\x80\x8b": "Zero-width space (U+200B)",
}

for seq, name in suspicious.items():
    if seq in content:
        print(f"⚠️  Gefunden: {name} bei Byte-Position {content.find(seq)}")

# Entferne sie alle
cleaned = (
    content.replace(b"\xef\xbb\xbf", b"")
    .replace(b"\x00", b"")
    .replace(b"\xa0", b" ")
    .replace(b"\xe2\x80\x8b", b"")
)

with open(output_file, "wb") as f:
    f.write(cleaned)

print(f"✅ Bereinigt gespeichert als: {output_file}")
