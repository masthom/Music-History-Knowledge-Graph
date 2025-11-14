from rdflib import Graph, Namespace, URIRef

# ==== Einstellungen ====
TTL_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"

# ==== Namespaces ====
mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
schema = Namespace("https://schema.org/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

# ==== RDF laden ====
print(f"Lade RDF-Datei: {TTL_FILE}")
g = Graph()
g.parse(TTL_FILE, format="ttl")
print(f"Triples insgesamt: {len(g)}")

# ==== Benutzerwahl ====
print("\nWas möchtest du extrahieren?")
print("1 = Komponist(en)")
print("2 = Werk(e)")
print("3 = RowClass(es)")
wahl = input("Bitte wählen (1/2/3): ").strip()

if wahl not in {"1", "2", "3"}:
    print("Ungültige Eingabe.")
    exit()

namen = input("Gib eine oder mehrere lokale IDs durch Komma getrennt ein (z.B. AlbanBerg, ArnoldSchoenberg):\n> ").strip()
ids = [n.strip() for n in namen.split(",") if n.strip()]

# ==== Subgraph erstellen ====
subgraph = Graph()
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

for local_id in ids:
    entity = mhg[local_id]
    if wahl == "1":
        # Komponist: alle Triples, die diesen Komponisten betreffen
        for s, p, o in g.triples((entity, None, None)):
            subgraph.add((s, p, o))
        for s, p, o in g.triples((None, None, entity)):
            subgraph.add((s, p, o))
        # ggf. Werke hinzufügen
        for _, _, work in g.triples((entity, frbr.creatorOf, None)):
            for s, p, o in g.triples((work, None, None)):
                subgraph.add((s, p, o))

    elif wahl == "2":
        # Werk: alle Triples, die dieses Werk betreffen
        for s, p, o in g.triples((entity, None, None)):
            subgraph.add((s, p, o))
        for s, p, o in g.triples((None, None, entity)):
            subgraph.add((s, p, o))

    elif wahl == "3":
        # RowClass: alle zugehörigen rowForms finden
        for s, p, o in g.triples((None, mhg.hasRowClass, entity)):
            subgraph.add((s, p, o))
            for s2, p2, o2 in g.triples((s, None, None)):
                subgraph.add((s2, p2, o2))
        # auch alle Eigenschaften der RowClass selbst
        for s, p, o in g.triples((entity, None, None)):
            subgraph.add((s, p, o))

# ==== Ausgabe ====
out_file = f"subgraph_{'_'.join(ids)}.ttl"
subgraph.serialize(out_file, format="turtle")
print(f"\n✅ Subgraph gespeichert als: {out_file}")
print(f"Enthält {len(subgraph)} Triples.")

