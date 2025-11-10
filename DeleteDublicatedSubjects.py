from rdflib import Graph

from rdflib import Namespace

# TTL-Datei laden
input_file = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
output_file = "merged_triples.ttl"

# Graph einlesen
g = Graph()
g.parse(input_file, format="ttl")

print(f"Triples geladen: {len(g)}")

mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
dcterms = Namespace("http://purl.org/dc/terms/")

g.bind("mhg", mhg)
g.bind("dcterms", dcterms)


# Graph neu serialisieren – rdflib gruppiert automatisch gleiche Subjekte
g.serialize(destination=output_file, format="turtle")

print(f"Zusammengefasster Graph gespeichert als {output_file}")
