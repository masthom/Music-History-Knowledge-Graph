import re
import sys

def count_rowclass_triples(ttl_file):
    """
    Zählt alle Tripel der Form:
    <subject> a mhg:rowClass .
    """

    pattern = re.compile(r"##not yet detected ,$")
    count = 0
    matches = []

    with open(ttl_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if pattern.search(line):
                count += 1
                matches.append((i, line.strip()))

    print(f"✅ Datei: {ttl_file}")
    print(f"📊 Gefundene '##not yet detected ,': {count}")

    if count > 0:
        print("\n🔎 Beispielzeilen:")
        for lno, text in matches[:5]:
            print(f"  Zeile {lno}: {text}")

    return count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python count_rowclass_triples.py <input.ttl>")
        sys.exit(1)

    count_rowclass_triples(sys.argv[1])


