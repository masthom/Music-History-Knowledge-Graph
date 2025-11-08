from rdflib import Graph
g = Graph()
g.parse("MusicHistoryGraph_TwelveToneMusic_TEST_utf8.ttl", format="turtle")
print("✅ Parsed successfully. Triples:", len(g))

