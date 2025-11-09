import re
from pathlib import Path

orig_file = Path("MusicHistoryGraph_TwelveToneMusic_NEW.ttl")
norm_file = Path("MusicHistoryGraph_TwelveToneMusic_NORMALIZED_SAFE.ttl")

orig = orig_file.read_text(encoding="utf-8").splitlines()
norm = norm_file.read_text(encoding="utf-8").splitlines()

diffs = []
for i, (o, n) in enumerate(zip(orig, norm), start=1):
    if o != n:
        # ignoriere reine URI-Änderungen wie mhg:XXX -> mhg:YYY
        if re.search(r"mhg:[A-Za-z0-9_]+", o) and re.search(r"mhg:[A-Za-z0-9_]+", n):
            continue
        diffs.append((i, o, n))

print(f"🔍 {len(diffs)} verdächtige Zeilen mit Änderungen außerhalb von URIs gefunden:\n")
for i, o, n in diffs[:30]:
    print(f"Zeile {i}:")
    print(f"  ALT: {o.strip()}")
    print(f"  NEU: {n.strip()}\n")

if len(diffs) > 30:
    print(f"... und {len(diffs)-30} weitere Zeilen.")
