# diagnose_ttl_issues.py
# Python 3.x
import re
import sys
from collections import Counter

ttl_file = "Composers_Works_Rows_SerialAnalyzer_TEST.ttl"

from rdflib import Graph

ttl_data = """
@prefix mhg: <http://example.org/mhg#> .
@prefix frbr: <http://purl.org/vocab/frbr/core#> .
@prefix schema: <http://schema.org/> .

mhg:theodorWiesengrundAdorno a mhg:composer ;
    frbr:creatorOf mhg:Adorno_Totenlied_auf_den_Kater ;
    schema:name "Adorno, Theodor W." .
"""

g = Graph()
g.parse(data=ttl_data, format="turtle")
print("✅ Erfolgreich geladen!")


def show_bytes(s):
    return " ".join(f"{b:02x}" for b in s)

def codepoints(s):
    return " ".join(f"U+{ord(ch):04X}" for ch in s)

with open(ttl_file, "rb") as f:
    data_bytes = f.read()

# 1) BOM check
if data_bytes.startswith(b'\xef\xbb\xbf'):
    print("⚠️ UTF-8 BOM gefunden (EF BB BF). Entfernen empfohlen.\n")

# 2) show first 200 bytes hex for quick look
print("### Erste 200 Bytes (hex) ###")
print(show_bytes(data_bytes[:200]))
print()

# 3) decode with utf-8 with replacement to see if there are invalid sequences
text = data_bytes.decode("utf-8", errors="replace")

lines = text.splitlines()
print(f"Datei hat {len(lines)} Zeilen\n")

# 4) Find non-printable / suspicious characters
suspicious = []
for i, line in enumerate(lines, start=1):
    for j, ch in enumerate(line):
        if ord(ch) < 32 and ch not in ("\t", "\n", "\r"):
            suspicious.append((i, j+1, ch, ord(ch)))
        # non-breaking space or zero-width etc.
        if ord(ch) in (0x00A0, 0x200B, 0x200C, 0x200D, 0xFEFF):
            suspicious.append((i, j+1, ch, ord(ch)))

if suspicious:
    print("⚠️ Nicht-druckbare oder spezielle Whitespace-Zeichen gefunden (Zeile,Spalte,Code):")
    for item in suspicious[:20]:
        print(f"  Zeile {item[0]} Spalte {item[1]} -> U+{item[3]:04X}")
    print()

# 5) Print repr and codepoints around the reported area (first 60 lines)
context_start = 1
context_end = min(120, len(lines))
print(f"### Zeilen {context_start}–{context_end} (repr + codepoints jeweils) ###")
for i in range(context_start-1, context_end):
    l = lines[i]
    print(f"{i+1:04d}: repr: {repr(l)}")
    if len(l)>0:
        print(f"      codepts: {codepoints(l)}")
print()

# 6) Check balancing of quotes and brackets for whole file and per-line
def balance_counts(s):
    cnt = Counter()
    cnt['"'] = s.count('"')
    cnt["'"] = s.count("'")
    cnt['['] = s.count('[')
    cnt[']'] = s.count(']')
    cnt['('] = s.count('(')
    cnt[')'] = s.count(')')
    cnt['{'] = s.count('{')
    cnt['}'] = s.count('}')
    return cnt

global_counts = balance_counts(text)
print("### Global counts (quotes & brackets) ###")
for k in ['"', "'", '[', ']', '(', ')', '{', '}']:
    print(f"  {k}: {global_counts[k]}")
print()

# 7) Look for lines that likely miss trailing dot (heuristic)
no_dot_lines = []
for i, l in enumerate(lines, start=1):
    # line ends with quote and possibly spaces but no dot, and next non-empty line starts with 'mhg:' or prefix
    if re.search(r'"\s*$', l):
        # find next non-empty line
        nxt = None
        for j in range(i, min(i+6, len(lines))):
            if lines[j].strip():
                nxt = lines[j].strip()
                break
        if nxt and re.match(r'^(mhg:|[a-zA-Z][\w\-]*:)', nxt):
            no_dot_lines.append(i)
if no_dot_lines:
    print("⚠️ Mögliche fehlende '.' am Ende folgender Zeilen (heuristisch):")
    for ln in no_dot_lines[:30]:
        print(f"  Zeile {ln}: {lines[ln-1].rstrip()!r}")
    print()

# 8) Find CURIE/localnames with illegal characters (look for mhg:... tokens)
bad_curie = []
curie_pattern = re.compile(r'\b([A-Za-z][\w\-]*)\:([^\s\)\]\;,\.\"]+)')
for i, l in enumerate(lines, start=1):
    for m in curie_pattern.finditer(l):
        prefix, local = m.group(1), m.group(2)
        # localname must not contain spaces or control chars, disallow certain chars
        if re.search(r"[\'\"\s\(\)\,;<>\\\{\}]", local):
            bad_curie.append((i, prefix+":"+local))
if bad_curie:
    print("⚠️ Gefundene CURIEs mit problematischen Zeichen:")
    for i, cur in bad_curie[:40]:
        print(f"  Zeile {i}: {cur}")
    print()

# 9) Per-line quick parse until failure to show exact failing line index (sauberer)
from rdflib import Graph
snippet = ""
for i, line in enumerate(lines, start=1):
    snippet += line + "\n"
    try:
        g = Graph()
        g.parse(data=snippet, format="turtle")
    except Exception as e:
        print(f"\nParser stürzt beim schrittweisen Parsen an Zeile {i} ab:")
        print("  Exception:", e)
        context_from = max(1, i-6)
        context_to = min(len(lines), i+2)
        print(f"  Kontext Zeilen {context_from}–{context_to}:")
        for k in range(context_from, context_to+1):
            print(f"   {k:04d}: {repr(lines[k-1])}")
        break
else:
    print("✅ Schrittweises Parsen erfolgreich (kein Fehler gefunden).")

print("\nFertig mit Diagnose. Falls du magst, poste hier die ausgegebenen Warnungen/Zeilen und ich helfe beim Beheben.")
