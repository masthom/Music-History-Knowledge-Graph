from rdflib import Graph, Namespace, RDF, RDFS, Literal
import networkx as nx

# ==== Einstellungen ====
input_file = "MusicHistoryGraph_TwelveToneMusic.ttl"   # Eingabe-Datei
output_file = "MHG_TwelveToneMusic.graphml"  # Ausgabe-Datei
limit_triples = None                  # z. B. 5000 oder None für alle

# ==== RDF-Datei laden ====
print(f"📥 Lade RDF-Datei: {input_file}")
g = Graph()
g.parse(input_file)
print(f"✅ Geladene Triples: {len(g)}")

# ==== Namespaces ====
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("http://schema.org/")

# ==== NetworkX-Graph erstellen ====
G = nx.DiGraph()

# ==== Labels und Attribute sammeln ====
node_labels = {}
node_attrs = {}

for s, p, o in g:
    # Triples limitieren
    if limit_triples and len(G.edges()) > limit_triples:
        break

    s_str, p_str, o_str = str(s), str(p), str(o)

    # Literal-Objekte als Attribut behandeln
    if isinstance(o, Literal):
        if s_str not in node_attrs:
            node_attrs[s_str] = {}
        node_attrs[s_str][p_str] = str(o)

        # Label-Properties erkennen
        if p in [RDFS.label, FOAF.name, SCHEMA.name]:
            node_labels[s_str] = str(o)
        continue

    # Beziehungen als Kante hinzufügen
    G.add_node(s_str)
    G.add_node(o_str)
    G.add_edge(s_str, o_str, label=p_str)

# ==== Labels anwenden ====
for n in G.nodes():
    label = node_labels.get(n, n.split("/")[-1])  # Fallback: letzter Teil der URI
    attrs = node_attrs.get(n, {})
    G.nodes[n]["label"] = label
    # Weitere Attribute hinzufügen
    for k, v in attrs.items():
        G.nodes[n][k] = v

print(f"🔗 Knoten: {len(G.nodes())}, Kanten: {len(G.edges())}")

# ==== GraphML speichern ====
nx.write_graphml(G, output_file)
print(f"💾 Exportiert als: {output_file}")
