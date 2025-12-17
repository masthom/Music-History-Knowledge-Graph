from rdflib import Graph, Namespace, URIRef, BNode

# ========== KONFIGURATION =====================================================

TTL_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
OUTPUT_FILE = "subgraph_rf_ip_rotations.ttl"

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

# --- Blank Node Normalisierung ---
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


# === Schritt 2: Triples für rf_* sammeln =====================================

visited_bnodes = set()
ip_nodes = set()
rotation_nodes = set()

def add_subject_triples(subject):
    """Alle Triples mit subject als Subjekt hinzufügen, Blank Nodes ausdehnen."""
    for s, p, o in g.triples((subject, None, None)):
        o2 = mat(o)
        sub.add((s, p, o2))

        if isinstance(o, BNode):
            expand_blank(o, visited_bnodes)

        # Neue Kandidaten finden:
        # rf_* -> ip_*
        if p == MHG.hasIntervalPattern and isinstance(o, URIRef):
            if str(o).startswith(str(MHG) + "ip_"):
                ip_nodes.add(o)

        # ip_* -> rotationGroup_*
        if p == MHG.hasRotationGroup and isinstance(o, URIRef):
            if str(o).startswith(str(MHG) + "rotationGroup_"):
                rotation_nodes.add(o)


# --- Step 2a: rf_* Triples aufnehmen ---
for rf in rf_nodes:
    add_subject_triples(rf)

print(f"Gefundene Interval Patterns (ip_*): {len(ip_nodes)}")


# === Schritt 3: Triples für ip_* sammeln =====================================

for ip in ip_nodes:
    add_subject_triples(ip)

print(f"Gefundene Rotation Groups (rotationGroup_*): {len(rotation_nodes)}")


# === Schritt 4: Triples für rotationGroup_* sammeln ===========================

for rot in rotation_nodes:
    add_subject_triples(rot)


# === Ausgabe ==================================================================

sub.serialize(OUTPUT_FILE, format="turtle")
print(f"Subgraph gespeichert als {OUTPUT_FILE}")
