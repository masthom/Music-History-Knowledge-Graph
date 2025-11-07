from rdflib import Graph

ttl_file = "Composers_Works_Rows_SerialAnalyzer_TEST.ttl"

with open(ttl_file, encoding="utf-8") as f:
    lines = f.readlines()

print(f"Prüfe {len(lines)} Zeilen...")

for i in range(0, len(lines), 50):
    snippet = "".join(lines[:i+50])
    try:
        g = Graph()
        g.parse(data=snippet, format="turtle")
    except Exception as e:
        print(f"\n❌ Fehler zwischen Zeile {i-49 if i>0 else 1} und {i+50}: {e}")
        print("Letzte 5 Zeilen vor Fehler:")
        for l in lines[i+45:i+50]:
            print(" ", l.strip())
        break
else:
    print("✅ Kein Syntaxfehler gefunden (alle Blöcke erfolgreich gelesen).")
