from rdflib import Graph

ttl_file = "MusicHistoryGraph_TwelveToneMusic_TEST_clean.ttl"

lines = []
with open(ttl_file, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        lines.append(line)
        snippet = "".join(lines)
        g = Graph()
        try:
            g.parse(data=snippet, format="turtle")
        except Exception as e:
            print(f"❌ Parserfehler bei Zeile {i}: {e}")
            print("→ Kontext:")
            context = lines[max(0, i-3):i+2]
            for j, c in enumerate(context, start=i-len(context)+1):
                print(f" {j:4}: {c.strip()}")
            break
