# ttl_to_graphml_yed_final_fixed.py
from rdflib import Graph, URIRef, Literal
import xml.etree.ElementTree as ET
import hashlib
import re

# ----- Einstellungen -----
input_ttl = "MusicHistoryGraph_TwelveToneMusic.ttl"
output_graphml = "MHG_TwelveToneMusic_Yed.graphml"

# ----- Helfer -----
def shorten_uri(node):
    s = str(node)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s:
        return s.rstrip("/").split("/")[-1]
    return s

def make_node_id(s):
    h = hashlib.md5(s.encode("utf-8")).hexdigest()[:10]
    return "n_" + h

def sanitize_key(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name)

# ----- RDF laden -----
g = Graph()
g.parse(input_ttl, format="turtle")
print(f"Triples loaded: {len(g)}")

nodes = {}
edges = []

for s, p, o in g:
    s_str = str(s)
    p_short = shorten_uri(p)
    if s_str not in nodes:
        nodes[s_str] = {"id": make_node_id(s_str), "label": None, "attrs": {}}

    if isinstance(o, Literal):
        key = sanitize_key(p_short)
        nodes[s_str]["attrs"][key] = str(o)
        if key.lower() in ("label", "name", "title", "prefLabel"):
            nodes[s_str]["label"] = str(o)
    elif isinstance(o, URIRef):
        o_str = str(o)
        if o_str not in nodes:
            nodes[o_str] = {"id": make_node_id(o_str), "label": None, "attrs": {}}
        edges.append((s_str, o_str, p_short))

for uri, info in nodes.items():
    if not info["label"]:
        info["label"] = shorten_uri(uri)

print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

# ----- GraphML -----
ET.register_namespace("", "http://graphml.graphdrawing.org/xmlns")
ET.register_namespace("y", "http://www.yworks.com/xml/graphml")

NS = "http://graphml.graphdrawing.org/xmlns"
YNS = "http://www.yworks.com/xml/graphml"

graphml = ET.Element(ET.QName(NS, "graphml"))  # <--- kein xmlns:y mehr hier

# ----- Keys -----
ET.SubElement(graphml, "key", id="d0", **{"for": "node", "yfiles.type": "nodegraphics"})
ET.SubElement(graphml, "key", id="d1", **{"for": "edge", "yfiles.type": "edgegraphics"})
ET.SubElement(graphml, "key", id="d_label", **{"for": "node", "attr.name": "label", "attr.type": "string"})
ET.SubElement(graphml, "key", id="d_elabel", **{"for": "edge", "attr.name": "label", "attr.type": "string"})

all_attr_keys = set()
for info in nodes.values():
    all_attr_keys.update(info["attrs"].keys())

attr_key_map = {}
for i, attr in enumerate(sorted(all_attr_keys)):
    key_id = f"d_attr_{i}"
    attr_key_map[attr] = key_id
    ET.SubElement(graphml, "key", id=key_id, **{"for": "node", "attr.name": attr, "attr.type": "string"})

graph = ET.SubElement(graphml, "graph", edgedefault="directed")

# ----- Nodes -----
for uri, info in nodes.items():
    n = ET.SubElement(graph, "node", id=info["id"])

    d_label = ET.SubElement(n, "data", key="d_label")
    d_label.text = info["label"]

    d_graphics = ET.SubElement(n, "data", key="d0")
    shape = ET.SubElement(d_graphics, ET.QName(YNS, "ShapeNode"))
    node_label = ET.SubElement(shape, ET.QName(YNS, "NodeLabel"))
    node_label.text = info["label"]
    node_label.set("fontSize", "12")

    for attr, val in info["attrs"].items():
        keyid = attr_key_map.get(attr)
        if keyid:
            d_attr = ET.SubElement(n, "data", key=keyid)
            d_attr.text = val

# ----- Edges -----
for i, (s_uri, o_uri, pred) in enumerate(edges):
    e = ET.SubElement(graph, "edge", id=f"e{i}", source=nodes[s_uri]["id"], target=nodes[o_uri]["id"])

    d_elabel = ET.SubElement(e, "data", key="d_elabel")
    d_elabel.text = pred

    d_graph = ET.SubElement(e, "data", key="d1")
    poly = ET.SubElement(d_graph, ET.QName(YNS, "PolyLineEdge"))
    edge_label = ET.SubElement(poly, ET.QName(YNS, "EdgeLabel"))
    edge_label.text = pred
    edge_label.set("fontSize", "11")

# ----- Schreiben -----
tree = ET.ElementTree(graphml)
tree.write(output_graphml, encoding="utf-8", xml_declaration=True)
print(f"✅ GraphML geschrieben: {output_graphml}")
