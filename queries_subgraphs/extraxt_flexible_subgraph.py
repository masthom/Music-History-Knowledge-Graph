from rdflib import Graph, Namespace

# === Datei & Namespaces ===
TTL_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"

mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
schema = Namespace("https://schema.org/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

# === RDF laden ===
print(f"Lade RDF-Datei: {TTL_FILE}")
g = Graph()
g.parse(TTL_FILE, format="ttl")
print(f"Triples insgesamt: {len(g)}\n")

# === Benutzereingabe ===
print("Was möchtest du extrahieren? (Mehrfachauswahl möglich)")
print("1 = Komponisten  |  2 = Werke  |  3 = RowClasses")
wahl = input("Bitte wähle z. B. 1,2 oder 1,3: ").strip()
wahl_set = {x.strip() for x in wahl.split(",") if x.strip() in {"1", "2", "3"}}

if not wahl_set:
    print("Keine gültige Auswahl. Abbruch.")
    exit()

namen = input(
    "Gib lokale IDs (ohne Präfix) durch Komma getrennt ein, z. B.\n"
    "AlbanBerg, ArnoldSchoenberg, AntonWebern, AB_Lulu, 1_4_9_4_9_1_4_11_3_11_2\n> "
).strip()
ids = [n.strip() for n in namen.split(",") if n.strip()]

# === Subgraph erzeugen ===
subgraph = Graph()
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

def add_all_triples_about(entity):
    """Fügt alle Tripel hinzu, in denen entity Subjekt oder Objekt ist."""
    for s, p, o in g.triples((entity, None, None)):
        subgraph.add((s, p, o))
    for s, p, o in g.triples((None, None, entity)):
        subgraph.add((s, p, o))


for local_id in ids:
    entity = mhg[local_id]

    # --- Komponist ---
    if "1" in wahl_set:
        for s, p, o in g.triples((entity, None, None)):
            subgraph.add((s, p, o))
        for s, p, o in g.triples((None, None, entity)):
            subgraph.add((s, p, o))

        # verbundene Werke ergänzen
        for _, _, work in g.triples((entity, frbr.creatorOf, None)):
            add_all_triples_about(work)

    # --- Werk ---
    if "2" in wahl_set:
        add_all_triples_about(entity)

        # evtl. Komponisten ergänzen
        for composer in g.objects(entity, frbr.created):
            add_all_triples_about(composer)

    # --- RowClass ---
    if "3" in wahl_set:
        # Eigenschaften der RowClass selbst
        add_all_triples_about(entity)

        # alle RowForms, die zu dieser Klasse gehören
        for rowform in g.subjects(mhg.hasRowClass, entity):
            add_all_triples_about(rowform)

# === Ausgabe ===
out_file = f"subgraph_{'_'.join(ids)}.ttl"
subgraph.serialize(out_file, format="turtle")

print(f"\n✅ Subgraph gespeichert als: {out_file}")
print(f"Enthält {len(subgraph)} Triples.")
