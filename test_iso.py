from rdflib import Graph
g = Graph()
g.parse("test_iso.ttl", format="turtle")
print("✅ OK, Triples:", len(g))
