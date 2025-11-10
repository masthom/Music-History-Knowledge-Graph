import re

with open("MusicHistoryGraph_TwelveToneMusic_Complete.ttl", encoding="utf-8") as f:
    data = f.read()

pattern = re.compile(
    r"""mhg:(?P<id>[A-Za-z0-9_]+)\s+a\s+mhg:rowForm;\s*mhg:hasRowClass\s+mhg:(?P<class>[A-Za-z0-9_]+)\s*\.\s*
mhg:(?P=id)\s+mhg:manifestedIn\s+\[
(?P<block>[\s\S]*?)
\]\s*\.""",
    re.MULTILINE | re.VERBOSE
)

replacement = (
    r"mhg:\g<id> a mhg:rowForm; "
    r"mhg:hasRowClass mhg:\g<class> ; "
    r"mhg:manifestedIn [\g<block>] ."
)

merged_data = re.sub(pattern, replacement, data)

with open("merged.ttl", "w", encoding="utf-8") as f:
    f.write(merged_data)

print("✅ Zusammenführung abgeschlossen – Datei 'merged.ttl' erstellt.")
