import re
import sys
from collections import defaultdict

def count_entity_types(ttl_file):
    """
    Zählt alle Tripel der Form:
      <subject> a mhg:<Typ> .
    für ausgewählte Typen (composer, composition, compositionPart, rowClass, rowForm).
    """

    # Suchmuster für RDF-Typen
    types_to_count = [
        "mhg:composer",
        "mhg:composition",
        "mhg:compositionPart",
        "mhg:rowClass",
        "mhg:rowForm",
    ]

    # Regex vorbereiten (alle Typen in einer Zeile prüfen)
    pattern = re.compile(
        r"\b[a-zA-Z0-9_]+:\S*\s+a\s+(mhg:(?:composer|composition|compositionPart|rowClass|rowForm))\b"
    )

    counts = defaultdict(int)
    examples = defaultdict(list)

    with open(ttl_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            match = pattern.search(line)
            if match:
                t = match.group(1)
                counts[t] += 1
                if len(examples[t]) < 5:
                    examples[t].append((i, line.strip()))

    print(f"✅ Datei: {ttl_file}")
    print("=" * 60)
    print("📊 Übersicht über RDF-Typen (Tripel mit 'a mhg:<Typ>')")
    print("=" * 60)

    total = 0
    for t in types_to_count:
        c = counts[t]
        total += c
        print(f"{t:<25} {c:>8}")

    print("-" * 60)
    print(f"{'GESAMT':<25} {total:>8}")

    print("\n🔎 Beispielzeilen (max. 5 pro Typ):")
    for t in types_to_count:
        if examples[t]:
            print(f"\n🧩 {t}:")
            for lno, text in examples[t]:
                print(f"  Zeile {lno}: {text}")

    return counts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung:")
        print("  python count_entity_types.py <input.ttl>")
        sys.exit(1)

    count_entity_types(sys.argv[1])
