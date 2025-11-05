from rdflib import Graph
from pyvis.network import Network

# --- RDF-Datei laden ---
ttl_file = "MusicHistoryGraph_TwelveToneMusic.ttl"
g = Graph()
g.parse(ttl_file, format="turtle")
print(f"Triples loaded: {len(g)}")

# --- Graph aufbauen ---
net = Network(height="800px", width="100%", directed=True)
net.force_atlas_2based()

for s, p, o in g:
    s, p, o = str(s), str(p), str(o)
    net.add_node(s, label=s, title=s)
    net.add_node(o, label=o, title=o)
    net.add_edge(s, o, title=p)

# --- HTML-Datei schreiben ---
net.write_html("graph_full.html")
print("✅ Graph saved as graph_full.html — open it in your browser.")
