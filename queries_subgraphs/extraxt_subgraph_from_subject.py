from rdflib import Graph, URIRef
from collections import deque

# Datei und Format anpassen
INPUT_FILE = "Music-History-Knowledge-Graph/MusicHistoryGraph_TwelveToneMusic_CompleteAdjust.ttl"
OUTPUT_FILE = "subgraph_expanded.ttl"
START_URI = "http://music-history-graph.ch/twelve-tone-onto#Zender_Canto_IV"  # Start-URI
DEPTH = 1  # Anzahl der Schritte (z. B. 1 = direkte Nachbarn, 2 = Nachbarn der Nachbarn, ...)

# Graph laden
g = Graph()
g.parse(INPUT_FILE, format="turtle")

# Subgraph vorbereiten
subgraph = Graph()

# Warteschlange für BFS
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

    # Alle Tripel, bei denen current_node Subjekt ist
    for s, p, o in g.triples((current_node, None, None)):
        subgraph.add((s, p, o))
        if o not in visited and isinstance(o, URIRef):
            queue.append((o, depth + 1))
            visited.add(o)

    # Alle Tripel, bei denen current_node Objekt ist
    for s, p, o in g.triples((None, None, current_node)):
        subgraph.add((s, p, o))
        if s not in visited and isinstance(s, URIRef):
            queue.append((s, depth + 1))
            visited.add(s)

print(f"Gesammelte Tripel: {len(subgraph)}")

# Serialisieren (z. B. als Turtle)
subgraph.serialize(destination=OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
