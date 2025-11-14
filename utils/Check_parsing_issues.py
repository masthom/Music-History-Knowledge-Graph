from rdflib import Graph

file = "merged.ttl"

print(f"🔍 Überprüfe Datei: {file}")

try:
    g = Graph()
    g.parse(file, format="turtle")
    print("✅ Datei konnte vollständig geparst werden!")
except Exception as e:
    print("❌ Parserfehler erkannt:")
    print("="*70)
    print(e)
    print("="*70)

    # Schritt 2: Zeilenweise prüfen, um den genauen Ort zu finden
    print("\n🔎 Suche nach fehlerhafter Zeile ...")
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    temp_graph = Graph()
    buffer = ""
    for i, line in enumerate(lines, start=1):
        buffer += line
        try:
            temp_graph.parse(data=buffer, format="turtle")
        except Exception:
            print(f"\n⚠️  Parserfehler ab Zeile {i}:")
            print("----- Kontext (±3 Zeilen) -----")
            for j in range(max(0, i-3), min(len(lines), i+3)):
                print(f"{j+1:5}: {lines[j].rstrip()}")
            print("-------------------------------")
            break
