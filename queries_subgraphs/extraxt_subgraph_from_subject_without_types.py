from rdflib import Graph, URIRef, RDF
from collections import deque

# === Einstellungen ===
INPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "subgraph_expanded.ttl"
START_URI = "http://music-history-graph.ch/twelve-tone-onto#Webern_String_Trio_Op_20"
DEPTH = 2  # Tiefe der Nachbarschaft

# === Graph laden ===
g = Graph()
g.parse(INPUT_FILE, format="turtle")

# === Subgraph initialisieren und Namespaces übernehmen ===
subgraph = Graph()
for prefix, namespace in g.namespaces():
    subgraph.bind(prefix, namespace)

# === BFS vorbereiten ===
queue = deque()
visited = set()
start_node = URIRef(START_URI)
queue.append((start_node, 0))
visited.add(start_node)

print(f"Starte BFS von {START_URI} bis Tiefe {DEPTH} ...")

while queue:
    current_node, depth = queue.popleft()
    if depth > DEPTH:
        continue

    # Tripel, bei denen current_node Subjekt ist
    for s, p, o in g.triples((current_node, None, None)):
        if p == RDF.type:  # rdf:type überspringen
            continue
        subgraph.add((s, p, o))
        if o not in visited and isinstance(o, URIRef):
            queue.append((o, depth + 1))
            visited.add(o)

    # Tripel, bei denen current_node Objekt ist
    for s, p, o in g.triples((None, None, current_node)):
        if p == RDF.type:  # rdf:type überspringen
            continue
        subgraph.add((s, p, o))
        if s not in visited and isinstance(s, URIRef):
            queue.append((s, depth + 1))
            visited.add(s)

print(f"Gesammelte Tripel (ohne rdf:type): {len(subgraph)}")

# === Ausgabe speichern ===
subgraph.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
