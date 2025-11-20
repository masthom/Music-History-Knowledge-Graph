from rdflib import Graph, URIRef, BNode, RDF
from collections import deque

# === Einstellungen ===
INPUT_FILE = "Music-History-Knowledge-Graph/MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "subgraph_expanded_with_bags.ttl"
START_URI = "http://music-history-graph.ch/twelve-tone-onto#Krenek_Lamentatio_Jeremiae_Prophetae_Op_93"
DEPTH = 2  # BFS-Tiefe

# === Graph laden ===
g = Graph()
g.parse(INPUT_FILE, format="turtle")

# === Subgraph vorbereiten (mit Namespaces) ===
subgraph = Graph()
for prefix, namespace in g.namespaces():
    subgraph.bind(prefix, namespace)

# === BNode-Mapping für stabile Ausgaben ===
bnode_map = {}

def materialize_bnode(node):
    """
    Weist jedem echten Blank Node einen stabilen rdflib-BNode zu.
    Dadurch verschwinden alle []-Inline-Darstellungen.
    """
    if node not in bnode_map:
        bnode_map[node] = BNode()    # erzeugt _:b1, _:b2, ...
    return bnode_map[node]

# === Rekursive Expansion von Blank Nodes ===
def add_blank_node_triples(node, visited_bnodes):
    """
    Fügt alle Tripel eines Blank Node rekursiv hinzu
    und ersetzt alle BNodes durch materialisierte Varianten.
    """
    if node in visited_bnodes:
        return
    visited_bnodes.add(node)

    mat_node = materialize_bnode(node)

    for s, p, o in g.triples((node, None, None)):
        if p == RDF.type:
            continue

        s2 = materialize_bnode(s) if isinstance(s, BNode) else s
        if isinstance(o, BNode):
            o2 = materialize_bnode(o)
        else:
            o2 = o

        subgraph.add((s2, p, o2))

        if isinstance(o, BNode):
            add_blank_node_triples(o, visited_bnodes)

# === BFS vorbereiten ===
queue = deque()
visited = set()
visited_bnodes = set()

start_node = URIRef(START_URI)
queue.append((start_node, 0))
visited.add(start_node)

print(f"Starte BFS von {START_URI} bis Tiefe {DEPTH} ...")

# ========================
#   BFS MAIN LOOP
# ========================
while queue:
    current_node, depth = queue.popleft()
    if depth > DEPTH:
        continue

    # --- Ausgehende Tripel ---
    for s, p, o in g.triples((current_node, None, None)):
        if p == RDF.type:
            continue

        s2 = s
        o2 = materialize_bnode(o) if isinstance(o, BNode) else o
        subgraph.add((s2, p, o2))

        if isinstance(o, BNode):
            add_blank_node_triples(o, visited_bnodes)
        elif isinstance(o, URIRef) and o not in visited:
            queue.append((o, depth + 1))
            visited.add(o)

    # --- Eingehende Tripel ---
    for s, p, o in g.triples((None, None, current_node)):
        if p == RDF.type:
            continue

        s2 = materialize_bnode(s) if isinstance(s, BNode) else s
        o2 = o
        subgraph.add((s2, p, o2))

        if isinstance(s, BNode):
            add_blank_node_triples(s, visited_bnodes)
        elif isinstance(s, URIRef) and s not in visited:
            queue.append((s, depth + 1))
            visited.add(s)

print(f"Gesammelte Tripel (inkl. Blank Nodes, ohne rdf:type): {len(subgraph)}")

# === Speichern ===
subgraph.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
