from pathlib import Path
import re

input_path = Path("MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE_corr.ttl")
output_path = Path("MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE_corr_FIXED.ttl")

# Datei als Bytes laden (um auch unsichtbare Zeichen zu erwischen)
data = input_path.read_bytes()

# 1️⃣ Non-breaking spaces ersetzen (U+00A0)
data = data.replace(b"\xA0", b" ")

# 2️⃣ Als UTF-8-Text decodieren
text = data.decode("utf-8", errors="replace")

# 3️⃣ Fehlerhafte Zeilen mit „F@prefix“ oder ähnlichen Mustern korrigieren
fixed_lines = []
for line in text.splitlines():
    if re.match(r"^[A-Za-z]*@prefix", line):  # z. B. "F@prefix"
        line = re.sub(r"^[A-Za-z]*(@prefix)", r"\1", line)
    fixed_lines.append(line)

# 4️⃣ Speichern
output_path.write_text("\n".join(fixed_lines), encoding="utf-8")

print(f"✅ Reparatur abgeschlossen.\nEingabe:  {input_path.name}\nAusgabe:  {output_path.name}")
