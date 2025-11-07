from rdflib import Graph

ttl_file = "Composers_Works_Rows_SerialAnalyzer.ttl"

with open(ttl_file, encoding="utf-8") as f:
    lines = f.readlines()

print(f"Datei hat {len(lines)} Zeilen")

def try_parse(snippet):
    g = Graph()
    g.parse(data=snippet, format="turtle")

# Jetzt prüfen wir jede Zeile einzeln auf Problemstellen
snippet = ""
for i, line in enumerate(lines, start=1):
    snippet += line
    try:
        try_parse(snippet)
    except Exception as e:
        print(f"\n❌ Syntaxfehler in oder kurz vor Zeile {i}: {e}")
        print("→ Problemstelle:")
        for context_line in lines[max(0, i-5):i+2]:
            print(f"{lines.index(context_line)+1:>5}: {context_line.strip()}")
        break
else:
    print("✅ Keine Syntaxfehler gefunden.")
