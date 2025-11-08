from rdflib import Graph, Namespace
from difflib import SequenceMatcher

# === Datei laden ===
ttl_file = "MusicHistoryGraph_TwelveToneMusic_TEST_clean.ttl"

# === Namespaces ===
mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")

# === RDF-Graph laden ===
g = Graph()
g.parse(ttl_file, format="turtle")

# === Tripel sammeln ===
composer_to_works = {}
for composer, _, work in g.triples((None, frbr.creatorOf, None)):
    composer_to_works.setdefault(composer, set()).add(work)

work_to_composer = {}
for work, _, composer in g.triples((None, frbr.creator, None)):
    work_to_composer[work] = composer

# === Vergleichsfunktion ===
def similar(a, b, threshold=0.85):
    """Vergleicht zwei Strings und gibt True zurück, wenn sie sich stark ähneln."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

# === Konsistenzprüfung ===
missing_in_works = []
possible_typos = []

for composer, works in composer_to_works.items():
    for work in works:
        if work not in work_to_composer:
            # Prüfe, ob es ein ähnliches Werk gibt
            for candidate in work_to_composer:
                if similar(str(work), str(candidate)):
                    possible_typos.append((work, candidate))
                    break
            else:
                missing_in_works.append((composer, work))

print("\n=== Prüfungsergebnis ===")
if not missing_in_works and not possible_typos:
    print("✅ Alle Beziehungen sind konsistent.")
else:
    if missing_in_works:
        print("\n❌ Fehlende Gegenbeziehungen:")
        for c, w in missing_in_works:
            print(f"  - {w.split('#')[-1]} (von {c.split('#')[-1]}) fehlt als frbr:creator")
    if possible_typos:
        print("\n⚠️  Mögliche Tippfehler / Schreibabweichungen:")
        for w1, w2 in possible_typos:
            print(f"  - {w1.split('#')[-1]} ≈ {w2.split('#')[-1]}")
