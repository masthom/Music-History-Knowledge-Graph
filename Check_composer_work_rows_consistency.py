from rdflib import Graph, Namespace, RDF
from difflib import SequenceMatcher

# === Datei laden ===
ttl_file = "MusicHistoryGraph_TwelveToneMusic_NORMALIZED_SAFE.ttl"

# === Namespaces ===
mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
dcterms = Namespace("http://purl.org/dc/terms/")

# === RDF-Graph laden ===
g = Graph()
g.parse(ttl_file, format="turtle")

# === Hilfsfunktionen ===
def similar(a, b, threshold=0.85):
    """Vergleicht zwei Strings und gibt True zurück, wenn sie sich stark ähneln."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def local_name(uri):
    return str(uri).split("#")[-1]

# === 1. COMPOSER–WORK Beziehungen ===
composer_to_works = {}
for composer, _, work in g.triples((None, frbr.creatorOf, None)):
    composer_to_works.setdefault(composer, set()).add(work)

work_to_composer = {}
for work, _, composer in g.triples((None, frbr.creator, None)):
    work_to_composer[work] = composer

# === 2. ROWCLASS–WORK Beziehungen ===
rowclass_to_work = {}
for rowclass, _, work in g.triples((None, mhg.actualizedIn, None)):
    rowclass_to_work[rowclass] = work

# === 3. ROWFORM–ROWCLASS & ROWFORM–WORK Beziehungen ===
rowform_to_rowclass = {}
rowform_to_work = {}

for rowform, _, rowclass in g.triples((None, mhg.hasRowClass, None)):
    rowform_to_rowclass[rowform] = rowclass

for rowform, _, anon in g.triples((None, mhg.manifestedIn, None)):
    # Suche nach eingebettetem Blank Node, der auf ein Werk verweist
    for _, _, work in g.triples((anon, mhg.manifestedIn, None)):
        rowform_to_work[rowform] = work

# === PRÜFUNGEN ===
missing_in_works = []
possible_typos = []
missing_rowclass_targets = []
missing_rowform_targets = []

# 1️⃣ Komponisten–Werke
for composer, works in composer_to_works.items():
    for work in works:
        if work not in work_to_composer:
            for candidate in work_to_composer:
                if similar(str(work), str(candidate)):
                    possible_typos.append((work, candidate))
                    break
            else:
                missing_in_works.append((composer, work))

# 2️⃣ RowClass–Work
for rowclass, work in rowclass_to_work.items():
    if (work, RDF.type, mhg.composition) not in g and (work, RDF.type, frbr.work) not in g:
        missing_rowclass_targets.append((rowclass, work))

# 3️⃣ RowForm–RowClass & RowForm–Work
for rowform, rowclass in rowform_to_rowclass.items():
    if (rowclass, RDF.type, mhg.rowClass) not in g:
        missing_rowform_targets.append((rowform, rowclass))

for rowform, work in rowform_to_work.items():
    if (work, RDF.type, mhg.composition) not in g and (work, RDF.type, frbr.work) not in g:
        missing_rowform_targets.append((rowform, work))

# === AUSGABE ===
print("\n=== KONSISTENZBERICHT ===")

if not (missing_in_works or possible_typos or missing_rowclass_targets or missing_rowform_targets):
    print("✅ Alle Relationen sind konsistent.")
else:
    if missing_in_works:
        print("\n❌ Fehlende 'frbr:creator'-Beziehungen:")
        for c, w in missing_in_works:
            print(f"  - {local_name(w)} (von {local_name(c)}) fehlt als frbr:creator")

    if possible_typos:
        print("\n⚠️  Mögliche Tippfehler / Schreibabweichungen:")
        for w1, w2 in possible_typos:
            print(f"  - {local_name(w1)} ≈ {local_name(w2)}")

    if missing_rowclass_targets:
        print("\n❌ RowClasses mit ungültigem 'actualizedIn'-Ziel:")
        for r, w in missing_rowclass_targets:
            print(f"  - {local_name(r)} → {local_name(w)} (kein gültiges Werk)")

    if missing_rowform_targets:
        print("\n❌ RowForms mit ungültigem Ziel (RowClass oder Werk):")
        for r, t in missing_rowform_targets:
            print(f"  - {local_name(r)} → {local_name(t)} (nicht vorhanden oder falscher Typ)")
