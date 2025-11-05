from rdflib import Graph, URIRef, Literal
import networkx as nx
import hashlib

input_file = "MusicHistoryGraph_TwelveToneMusic.ttl"
output_file = "MHG_TwelveToneMusic.graphml"

print(f"📥 Lade RDF-Datei: {input_file}")
g = Graph()
g.parse(input_file, format="turtle")
print(f"✅ Geladene Triples: {len(g)}")

# --- Hilfsfunktionen ---
def make_id(uri):
    """Erzeugt stabile, yEd-kompatible Node-ID."""
    return "n_" + hashlib.md5(uri.encode("utf-8")).hexdigest()[:10]

def short_label(uri):
    """Liest lesbaren Labeltext aus URI oder Literal."""
    u = str(uri)
    if isinstance(uri, Literal):
        return str(uri)
    if "#" in u:
        return u.split("#")[-1]
    elif "/" in u:
        return u.split("/")[-1]
    return u

# --- Mapping ---
id_map = {}

def get_id(uri):
    """Mappt RDF-Resource auf interne GraphML-ID."""
    u = str(uri)
    if u not in id_map:
        id_map[u] = make_id(u)
    return id_map[u]

# --- Graph aufbauen ---
G = nx.DiGraph()

for s, p, o in g:
    if not isinstance(s, URIRef):
        continue  # ignoriere Blank Nodes

    sid = get_id(s)
    G.add_node(sid, label=short_label(s))

    if isinstance(o, URIRef):
        oid = get_id(o)
        G.add_node(oid, label=short_label(o))
        G.add_edge(sid, oid, label=short_label(p))
    elif isinstance(o, Literal):
        pred = short_label(p)
        # Speichere Literale als Node-Attribut
        G.nodes[sid][pred] = str(o)

print(f"📊 Knoten: {len(G.nodes())}, Kanten: {len(G.edges())}")

# --- Export nach GraphML ---
nx.write_graphml(G, output_file)
print(f"💾 Exportiert als: {output_file}")
print("✅ Öffne die Datei in yEd → Menü 'Layout → Organic' oder 'Hierarchical'")
