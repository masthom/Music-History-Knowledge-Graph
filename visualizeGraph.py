from rdflib import Graph
from pyvis.network import Network

# --- Datei laden ---
ttl_file = "rows_rowclasses7.ttl"  # Pfad zur TTL-Datei
g = Graph()
g.parse(ttl_file, format="turtle")

print(f"Triples loaded: {len(g)}")

# --- pyvis-Netzwerk vorbereiten ---
net = Network(height="800px", width="100%", notebook=False, directed=True)
net.force_atlas_2based()  # hübsches Layout

# --- Tripel in Knoten/Kanten umwandeln ---
for s, p, o in g:
    s, p, o = str(s), str(p), str(o)
    net.add_node(s, label=s, title=s)
    net.add_node(o, label=o, title=o)
    net.add_edge(s, o, title=p)

# --- Visualisierung speichern ---
net.show("graph_full.html")
