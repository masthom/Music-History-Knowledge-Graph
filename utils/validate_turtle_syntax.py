import sys
import re
from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax

def validate_turtle_syntax(file_path):
    print(f"🔍 Überprüfe Datei: {file_path}")
    g = Graph()
    try:
        g.parse(file_path, format="turtle")
        print("✅ Keine Syntaxfehler gefunden.")
    except BadSyntax as e:
        print("❌ Parserfehler erkannt:")
        print("=" * 70)
        print(str(e))
        print("=" * 70)

        # Zeilennummer aus Exception extrahieren
        m = re.search(r"at line (\d+)", str(e))
        if m:
            error_line = int(m.group(1))
            print(f"\n🔎 Vermuteter Fehler in Zeile {error_line} (±5 Zeilen Kontext):\n")

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            start = max(0, error_line - 6)
            end = min(len(lines), error_line + 5)
            for i in range(start, end):
                prefix = "👉" if i + 1 == error_line else "  "
                print(f"{prefix} {i+1:5d}: {lines[i].rstrip()}")
        else:
            print("⚠️ Keine Zeilennummer im Fehlertext gefunden.")
    except Exception as e:
        print("🚨 Unerwarteter Fehler:")
        print(str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python validate_turtle_syntax.py <Datei.ttl>")
    else:
        validate_turtle_syntax(sys.argv[1])
