from rdflib import Graph, URIRef, Literal
import xml.etree.ElementTree as ET

# === Konfiguration ===
input_ttl = "MusicHistoryGraph_TwelveToneMusic.ttl"
output_graphml = "MHG_TwelveToneMusic_Yed_color.graphml"

# Farben pro RDF-Typ (add your own)
type_colors = {
    "composer": "#ffcc00",
    "composition": "#66ccff",
    "work": "#99ff99",
    "person": "#ff9999",
    "RowClass": "#2a1aa2",
    "RowForm": "#fd1818"
}

# === RDF laden ===
g = Graph()
g.parse(input_ttl, format="ttl")
print("Triples loaded:", len(g))

# === GraphML-Struktur ===
graphml = ET.Element(
    "graphml",
    {
        "xmlns": "http://graphml.graphdrawing.org/xmlns",
        "xmlns:y": "http://www.yworks.com/xml/graphml",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation":
            "http://graphml.graphdrawing.org/xmlns "
            "http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd"
    }
)

# Keys für yEd
keys = [
    ("d0", "node", "nodegraphics"),
    ("d1", "edge", "edgegraphics")
]
for key_id, for_type, ytype in keys:
    ET.SubElement(graphml, "key", id=key_id, **{"for": for_type, "yfiles.type": ytype})

graph_elem = ET.SubElement(graphml, "graph", edgedefault="directed", id="G")

# === Hilfsfunktionen ===
def short_label(uri):
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s:
        return s.split("/")[-1]
    return s

def color_for(node_uri):
    for t in g.objects(node_uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")):
        for key in type_colors:
            if key.lower() in str(t).lower():
                return type_colors[key]
    return "#cccccc"  # default grey

# === Triples verarbeiten ===
edges = []
for s, p, o in g:
    # Filter: keine schema:sameAs-Kanten
    if "schema.org/sameAs" in str(p):
        continue

    if isinstance(o, URIRef):
        edges.append((s, o, p))

# === Knoten erzeugen ===
nodes = set([s for s, _, _ in edges] + [o for _, o, _ in edges])

for node in nodes:
    node_id = short_label(node)
    label = node_id
    color = color_for(node)

    node_elem = ET.SubElement(graph_elem, "node", id=node_id)
    data = ET.SubElement(node_elem, "data", key="d0")

    shape = ET.SubElement(data, "{http://www.yworks.com/xml/graphml}ShapeNode")
    ET.SubElement(shape, "{http://www.yworks.com/xml/graphml}Fill",
                  color=color, transparent="false")
    ET.SubElement(shape, "{http://www.yworks.com/xml/graphml}BorderStyle",
                  color="#000000", type="line", width="1.0")
    label_elem = ET.SubElement(shape, "{http://www.yworks.com/xml/graphml}NodeLabel")
    label_elem.text = label

# === Kanten erzeugen ===
for i, (s, o, p) in enumerate(edges):
    edge_id = f"e{i}"
    edge_elem = ET.SubElement(graph_elem, "edge", id=edge_id,
                              source=short_label(s), target=short_label(o))
    data = ET.SubElement(edge_elem, "data", key="d1")
    polyline = ET.SubElement(data, "{http://www.yworks.com/xml/graphml}PolyLineEdge")
    label = ET.SubElement(polyline, "{http://www.yworks.com/xml/graphml}EdgeLabel")
    label.text = short_label(p)

# === Speichern ===
tree = ET.ElementTree(graphml)
tree.write(output_graphml, encoding="utf-8", xml_declaration=True)
print(f"GraphML written to {output_graphml}")
