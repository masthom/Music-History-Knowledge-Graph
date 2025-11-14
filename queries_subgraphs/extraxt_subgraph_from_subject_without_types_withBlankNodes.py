from rdflib import Graph, URIRef, BNode, RDF
from collections import deque

# === Einstellungen ===
INPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "subgraph_expanded_with_bags.ttl"
START_URI = "http://music-history-graph.ch/twelve-tone-onto#1_1_1_1_1_1_1_1_1_1_1"
DEPTH = 1  # BFS-Tiefe

# === Graph laden ===
g = Graph()
g.parse(INPUT_FILE, format="turtle")

# === Subgraph vorbereiten (mit originalen Namespaces) ===
subgraph = Graph()
for prefix, namespace in g.namespaces():
    subgraph.bind(prefix, namespace)

# === Hilfsfunktion: alle Tripel eines Blank Nodes rekursiv sammeln ===
def add_blank_node_triples(node, visited_bnodes):
    """Fügt alle Tripel, die zu einem Blank Node gehören, rekursiv hinzu."""
    if node in visited_bnodes:
        return
    visited_bnodes.add(node)
    for s, p, o in g.triples((node, None, None)):
        if p == RDF.type:
            continue  # rdf:type überspringen
        subgraph.add((s, p, o))
        if isinstance(o, BNode):  # verschachtelte Blank Nodes
            add_blank_node_triples(o, visited_bnodes)

# === BFS vorbereiten ===
queue = deque()
visited = set()
visited_bnodes = set()

start_node = URIRef(START_URI)
queue.append((start_node, 0))
visited.add(start_node)

print(f"Starte BFS von {START_URI} bis Tiefe {DEPTH} ...")

while queue:
    current_node, depth = queue.popleft()
    if depth > DEPTH:
        continue

    # --- Ausgehende Tripel ---
    for s, p, o in g.triples((current_node, None, None)):
        if p == RDF.type:
            continue
        subgraph.add((s, p, o))
        if isinstance(o, BNode):
            add_blank_node_triples(o, visited_bnodes)
        elif isinstance(o, URIRef) and o not in visited:
            queue.append((o, depth + 1))
            visited.add(o)

    # --- Eingehende Tripel ---
    for s, p, o in g.triples((None, None, current_node)):
        if p == RDF.type:
            continue
        subgraph.add((s, p, o))
        if isinstance(s, BNode):
            add_blank_node_triples(s, visited_bnodes)
        elif isinstance(s, URIRef) and s not in visited:
            queue.append((s, depth + 1))
            visited.add(s)

print(f"Gesammelte Tripel (inkl. Blank Nodes, ohne rdf:type): {len(subgraph)}")

# === Speichern ===
subgraph.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
