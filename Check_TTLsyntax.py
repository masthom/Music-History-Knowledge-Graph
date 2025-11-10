import rdflib
import sys
import re

def validate_turtle_syntax(file_path):
    print(f"🔍 Überprüfe Datei: {file_path}\n")

    # Versuche komplettes Parsen mit rdflib
    g = rdflib.Graph()
    try:
        g.parse(file_path, format="turtle")
        print("✅ Keine Parserfehler gefunden – Datei ist syntaktisch korrekt.")
        return
    except Exception as e:
        print("❌ Parserfehler erkannt:")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

    # Fehlerzeile aus der Fehlermeldung extrahieren
    m = re.search(r"at line (\d+)", str(e))
    if not m:
        print("\n⚠️  Keine genaue Zeilenangabe im Fehler – führe heuristische Prüfung durch...\n")
        check_common_syntax_issues(file_path)
        return

    line_num = int(m.group(1))
    print(f"\n🔎 Suche nach fehlerhafter Zeile ({line_num}) ...\n")

    # Kontext anzeigen (±3 Zeilen)
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    start = max(0, line_num - 4)
    end = min(len(lines), line_num + 3)

    print("⚠️  Parserfehler ab Zeile", line_num, ":")
    print("----- Kontext (±3 Zeilen) -----")
    for i in range(start, end):
        prefix = "👉" if (i + 1) == line_num else "  "
        print(f"{prefix} {i+1:5d}: {lines[i].rstrip()}")
    print("-------------------------------\n")

    # Anschließend Heuristik starten
    check_common_syntax_issues(file_path, line_num)


def check_common_syntax_issues(file_path, around_line=None):
    print("🧩 Führe einfache Heuristik-Prüfungen durch...")
    problems = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        l = line.strip()

        # Fehlende Trennzeichen (wenn Zeile mit URI endet, aber kein Punkt/Semikolon)
        if re.match(r"^[a-zA-Z0-9_:-]+$", l) and not l.endswith((".", ";")):
            problems.append((i, "Möglicherweise fehlendes ';' oder '.' am Zeilenende"))

        # Ungeschlossene eckige oder geschweifte Klammern
        if l.count("[") != l.count("]"):
            problems.append((i, "Ungleichmäßige Anzahl '[' und ']'"))
        if l.count("{") != l.count("}"):
            problems.append((i, "Ungleichmäßige Anzahl '{' und '}'"))
        if '"' in l and l.count('"') % 2 != 0:
            problems.append((i, "Ungerade Anzahl von Anführungszeichen"))

    if not problems:
        print("✅ Keine typischen Syntaxfehler in Struktur gefunden.")
    else:
        print(f"⚠️  {len(problems)} mögliche Strukturfehler gefunden:")
        for ln, msg in problems:
            if around_line is None or abs(ln - around_line) <= 5:
                print(f"   Zeile {ln}: {msg}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validiert Turtle-Dateien auf Syntaxfehler.")
    parser.add_argument("file", help="Pfad zur TTL-Datei")
    args = parser.parse_args()
    validate_turtle_syntax(args.file)
