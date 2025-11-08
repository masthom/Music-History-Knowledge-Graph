from rdflib import Graph

def find_ttl_error(file_path):
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(1, len(lines) + 1):
        g = Graph()
        try:
            g.parse(data="".join(lines[:i]), format="turtle")
        except Exception as e:
            print(f"❌ Parserfehler bei Zeile {i}: {e}")
            print("→ Problemstelle:")
            start = max(0, i - 3)
            for j, line in enumerate(lines[start:i+2], start + 1):
                print(f"{j:5}: {line.rstrip()}")
            break
    else:
        print("✅ Datei vollständig parsebar!")

# Beispielaufruf:
if __name__ == "__main__":
    find_ttl_error("MusicHistoryGraph_TwelveToneMusic_TEST.ttl")
