# fix_encoding_to_utf8.py
# Liest eine fehlerhaft codierte Turtle-Datei und speichert sie als echtes UTF-8

input_file = "MusicHistoryGraph_TwelveToneMusic_TEST_clean.ttl"
output_file = "MusicHistoryGraph_TwelveToneMusic_TEST_utf8.ttl"

with open(input_file, "r", encoding="latin-1") as f:
    text = f.read()

# Datei sauber als UTF-8 ohne BOM speichern
with open(output_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print(f"✅ Neu kodiert gespeichert als: {output_file}")
