from rdflib import Graph
import networkx as nx

# RDF laden
g = Graph()
g.parse("rows_rowclasses7.ttl")

print(f"Triples loaded: {len(g)}")

# NetworkX-DiGraph erstellen
G = nx.DiGraph()

for s, p, o in g:
    G.add_node(str(s))
    G.add_node(str(o))
    G.add_edge(str(s), str(o), label=str(p))

# Als GEXF speichern (für Gephi / Gephi Lite)
nx.write_gexf(G, "graph_export.gexf")
print("✅ Exported as graph_export.gexf")
