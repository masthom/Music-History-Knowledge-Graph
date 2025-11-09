from rdflib import Graph

ttl_file = "MusicHistoryGraph_TwelveToneMusic_NORMALIZED.ttl"

lines = []
with open(ttl_file, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        lines.append(line)
        g = Graph()
        try:
            g.parse(data="".join(lines), format="turtle")
        except Exception as e:
            print(f"❌ Parserfehler bei Zeile {i}: {e}")
            print("→ Kontext:")
            for j, c in enumerate(lines[max(0, i-5):i+1], start=max(0, i-4)):
                print(f"{j+1:4}: {c.strip()}")
            break
