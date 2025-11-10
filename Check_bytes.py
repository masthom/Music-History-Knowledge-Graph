from pathlib import Path
import difflib
import unicodedata

# Eingabe-Dateien
file_ok = Path("MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE.ttl")
file_bad = Path("MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE_corr.ttl")

# Zeilen lesen (UTF-8)
ok_lines = file_ok.read_text(encoding="utf-8", errors="replace").splitlines()
bad_lines = file_bad.read_text(encoding="utf-8", errors="replace").splitlines()

diff = difflib.unified_diff(ok_lines, bad_lines, fromfile=file_ok.name, tofile=file_bad.name, n=3)

# Unterschiede ausgeben und auffällige Zeichen markieren
print("=== Unterschiede zwischen funktionierender und korrigierter TTL-Datei ===\n")

for line in diff:
    if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
        visible = ""
        for ch in line:
            if ch == "\t":
                visible += "\\t"
            elif ch == "\r":
                visible += "\\r"
            elif ch == "\n":
                visible += "\\n"
            elif ord(ch) < 32 or ord(ch) == 127:
                visible += f"[CTRL:{ord(ch)}]"
            elif ch not in " \t\n\r" and not ch.isprintable():
                visible += f"[U+{ord(ch):04X}]"
            else:
                visible += ch
        print(visible)

# Byteweise Analyse auf problematische Zeichen
print("\n=== Byteweise Analyse potenziell fehlerhafter Zeichen ===")

for path in [file_bad]:
    print(f"\nUntersuche: {path.name}")
    content = path.read_bytes()
    for i, b in enumerate(content):
        if b in (0xA0, 0xAD, 0xFE, 0xFF):  # NBSP, Soft hyphen, BOM
            print(f"⚠️  Verdächtiges Byte {b:#04x} bei Position {i}")
