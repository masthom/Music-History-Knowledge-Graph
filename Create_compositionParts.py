import re
from pathlib import Path

def insert_composition_parts_multiline(input_file, output_file):
    """
    Fügt neue Tripel <XYn> a frbr:work , mhg:compositionPart .
    direkt nach jedem frbr:hasPart-Block ein — egal, ob ein- oder mehrzeilig.
    """

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Muster, das auch über Zeilen hinweg funktioniert
    pattern = re.compile(
        r"(frbr:hasPart\s+(?:[\s\S]*?))(?:[.;])", re.MULTILINE
    )

    additions = []
    for match in pattern.finditer(content):
        block = match.group(1)

        # Alle URIs extrahieren
        uris = re.findall(r"mhg:[A-Za-z0-9_]+", block)
        if not uris:
            continue

        # Kontext für Einrückung
        indent = "    " if "\n" in block else ""

        new_triples = "\n".join(
            f"{indent}{uri} a frbr:work , mhg:compositionPart ." for uri in uris
        )

        additions.append((match.end(), "\n" + new_triples + "\n"))

    # Rückwärts einfügen, damit Indizes stabil bleiben
    output = content
    for pos, newtext in reversed(additions):
        output = output[:pos] + newtext + output[pos:]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print("✅ Ergänzung abgeschlossen:")
    print(f"   Eingabe:  {input_file}")
    print(f"   Ausgabe:  {output_file}")
    print(f"   {len(additions)} 'frbr:hasPart'-Blöcke ergänzt.")
    total_parts = sum(len(re.findall(r'mhg:[A-Za-z0-9_]+', a[1])) for a in additions)
    print(f"   Insgesamt {total_parts} neue compositionPart-Einträge hinzugefügt.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Verwendung:")
        print("  python insert_composition_parts_multiline.py <input.ttl> <output.ttl>")
        sys.exit(1)

    insert_composition_parts_multiline(sys.argv[1], sys.argv[2])
