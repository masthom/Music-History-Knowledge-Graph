import rdflib
from rdflib import URIRef, Literal
import xml.etree.ElementTree as ET

# === Farbig + geformt nach RDF-Typ ===
type_styles = {
    "composer": {"color": "#ffcc00", "shape": "diamond"},
    "composition": {"color": "#66ccff", "shape": "rectangle"},
    "work": {"color": "#99ff99", "shape": "parallelogram"},
    "rowclass": {"color": "#2a1aa2", "shape": "ellipse"},
    "rowform": {"color": "#fd1818", "shape":"ellipse"}
}

def style_for(uri):
    types = list(g.objects(uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")))
    for t in types:
        t_str = str(t).lower()
        for key, style in type_styles.items():
            if key.lower() in t_str.split("#")[-1].lower():
                return style

    return {"color": "#cccccc", "shape": "rectangle"}

def label_for(uri):
    label = g.value(uri, URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
    if label:
        return str(label)
    name = g.value(uri, URIRef("https://schema.org/name"))
    if name:
        return str(name)
    return uri.split("#")[-1].split("/")[-1]

def estimate_size(label):
    """Bestimme eine passende Knotengröße basierend auf Textlänge."""
    w = max(60, len(label) * 7)
    h = 30 + (len(label) // 15) * 10
    return w, h

# === Graph laden ===
g = rdflib.Graph()
g.parse("MusicHistoryGraph_TwelveToneMusic.ttl", format="turtle")
print(f"Triples loaded: {len(g)}")

# === GraphML-Grundstruktur ===
graphml = ET.Element(
    "graphml",
    {
        "xmlns": "http://graphml.graphdrawing.org/xmlns",
        "xmlns:y": "http://www.yworks.com/xml/graphml",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd",
    },
)
ET.SubElement(graphml, "key", {"id": "d0", "for": "node", "yfiles.type": "nodegraphics"})
ET.SubElement(graphml, "key", {"id": "d1", "for": "edge", "yfiles.type": "edgegraphics"})
graph = ET.SubElement(graphml, "graph", {"id": "G", "edgedefault": "directed"})

# === 1️⃣ Alle Knoten sammeln ===
uris = set()
for s, p, o in g:
    if isinstance(s, URIRef):
        uris.add(s)
    if isinstance(o, URIRef):
        uris.add(o)

print(f"Unique nodes detected: {len(uris)}")

# === 2️⃣ Knoten erzeugen ===
for uri in uris:
    style = style_for(uri)
    label = label_for(uri)
    width, height = estimate_size(label)

    node = ET.SubElement(graph, "node", {"id": str(uri)})
    data = ET.SubElement(node, "data", {"key": "d0"})
    shapeNode = ET.SubElement(data, "{http://www.yworks.com/xml/graphml}ShapeNode")

    ET.SubElement(shapeNode, "{http://www.yworks.com/xml/graphml}Geometry",
                  {"height": str(height), "width": str(width), "x": "0.0", "y": "0.0"})
    ET.SubElement(shapeNode, "{http://www.yworks.com/xml/graphml}Fill",
                  {"color": style["color"], "transparent": "false"})
    ET.SubElement(shapeNode, "{http://www.yworks.com/xml/graphml}BorderStyle",
                  {"color": "#000000", "type": "line", "width": "1.0"})
    ET.SubElement(shapeNode, "{http://www.yworks.com/xml/graphml}NodeLabel").text = label
    ET.SubElement(shapeNode, "{http://www.yworks.com/xml/graphml}Shape", {"type": style["shape"]})

# === 3️⃣ Kanten erzeugen (nur gültige URIs, keine Literale, keine sameAs) ===
edge_count = 0
for s, p, o in g:
    if isinstance(s, URIRef) and isinstance(o, URIRef) and "sameAs" not in str(p):
        if s in uris and o in uris:
            edge = ET.SubElement(graph, "edge", {"source": str(s), "target": str(o)})
            ET.SubElement(ET.SubElement(edge, "data", {"key": "d1"}),
                          "{http://www.yworks.com/xml/graphml}PolyLineEdge")
            edge_count += 1

print(f"Edges written: {edge_count}")

# === Speichern ===
tree = ET.ElementTree(graphml)
tree.write("output_yed_safe.graphml", encoding="utf-8", xml_declaration=True)
print("✅ output_yed_safe.graphml written successfully.")