from rdflib import Graph, Namespace, URIRef, BNode

# ========== KONFIGURATION =====================================================

TTL_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "subgraph_rf_Stravinsky_Movements.ttl"

MHG = Namespace("http://music-history-graph.ch/twelve-tone-onto#")

TARGET_OBJECT = MHG.Stravinsky_Movements
PROPERTY = MHG.manifestedIn

# ==============================================================================


# --- TTL laden ---
g = Graph()
g.parse(TTL_FILE, format="turtle")

# --- Subgraph vorbereiten ---
sub = Graph()
for prefix, ns in g.namespaces():
    sub.bind(prefix, ns)

# --- Blank Node normalisieren ---
bnode_map = {}

def mat(node):
    if isinstance(node, BNode):
        if node not in bnode_map:
            bnode_map[node] = BNode()
        return bnode_map[node]
    return node


def expand_blank(o, visited):
    """Rekursiv alle Triples eines Blank Nodes hinzufügen."""
    if o in visited:
        return
    visited.add(o)

    for s, p, o2 in g.triples((o, None, None)):
        s2 = mat(s)
        o3 = mat(o2)
        sub.add((s2, p, o3))

        if isinstance(o2, BNode):
            expand_blank(o2, visited)


# === Schritt 1: Reihenformen finden ==========================================

rf_nodes = set()

for s, p, o in g.triples((None, PROPERTY, TARGET_OBJECT)):
    s_str = str(s)
    if s_str.startswith(str(MHG) + "rf_"):
        rf_nodes.add(s)

print(f"Gefundene Reihenformen: {len(rf_nodes)}")


# === Schritt 2: Nur Triples hinzufügen, bei denen rf_node Subjekt ist =========

visited_bnodes = set()

for rf in rf_nodes:
    for s, p, o in g.triples((rf, None, None)):
        s2 = s
        o2 = mat(o)
        sub.add((s2, p, o2))

        if isinstance(o, BNode):
            expand_blank(o, visited_bnodes)


# === Ausgabe ==================================================================

sub.serialize(OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
