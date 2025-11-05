from rdflib import Graph, URIRef, Literal
import xml.etree.ElementTree as ET

# Eingabe und Ausgabe
input_file = "MusicHistoryGraph_TwelveToneMusic.ttl"
output_file = "MHG_TwelveToneMusic_Yed.graphml"

# RDF laden
g = Graph()
g.parse(input_file, format="turtle")

# XML-Namespaces
ET.register_namespace("", "http://graphml.graphdrawing.org/xmlns")
ET.register_namespace("y", "http://www.yworks.com/xml/graphml")

graphml = ET.Element("{http://graphml.graphdrawing.org/xmlns}graphml")

# Schlüsseldefinitionen hinzufügen (für Labels)
keys = [
    {"id": "d0", "for": "node", "attr.name": "label", "attr.type": "string"},
    {"id": "d1", "for": "edge", "attr.name": "label", "attr.type": "string"},
    {"id": "d2", "for": "node", "yfiles.type": "nodegraphics"},
    {"id": "d3", "for": "edge", "yfiles.type": "edgegraphics"},
]
for k in keys:
    key_elem = ET.SubElement(graphml, "key", k)

# Graph-Element
graph = ET.SubElement(graphml, "graph", edgedefault="directed")

def make_id(uri):
    return str(abs(hash(uri)))[:10]

# Knoten sammeln
nodes = {}
for s, p, o in g:
    if isinstance(s, URIRef):
        nodes[s] = True
    if isinstance(o, URIRef):
        nodes[o] = True

# Knoten erzeugen
for node_uri in nodes:
    node_id = make_id(node_uri)
    node = ET.SubElement(graph, "node", id=node_id)

    # Label aus RDF suchen
    label = None
    for _, p, o in g.triples((node_uri, None, None)):
        if any(p.endswith(x) for x in ["name", "label", "title"]):
            if isinstance(o, Literal):
                label = str(o)
                break

    if label is None:
        label = str(node_uri).split("/")[-1]

    # Sichtbares Label (für yEd)
    data_label = ET.SubElement(node, "data", key="d0")
    data_label.text = label

    data_graphics = ET.SubElement(node, "data", key="d2")
    node_label = ET.SubElement(
        data_graphics,
        "{http://www.yworks.com/xml/graphml}ShapeNode"
    )
    label_elem = ET.SubElement(
        node_label,
        "{http://www.yworks.com/xml/graphml}NodeLabel"
    )
    label_elem.text = label

# Kanten erzeugen
for s, p, o in g:
    if isinstance(s, URIRef) and isinstance(o, URIRef):
        edge = ET.SubElement(graph, "edge",
                             source=make_id(s),
                             target=make_id(o))

        label = str(p).split("/")[-1]

        data_label = ET.SubElement(edge, "data", key="d1")
        data_label.text = label

        data_graphics = ET.SubElement(edge, "data", key="d3")
        edge_label = ET.SubElement(
            data_graphics,
            "{http://www.yworks.com/xml/graphml}PolyLineEdge"
        )
        label_elem = ET.SubElement(
            edge_label,
            "{http://www.yworks.com/xml/graphml}EdgeLabel"
        )
        label_elem.text = label

# Datei speichern
tree = ET.ElementTree(graphml)
tree.write(output_file, encoding="utf-8", xml_declaration=True)

print(f"GraphML mit sichtbaren Labels gespeichert als {output_file}")
