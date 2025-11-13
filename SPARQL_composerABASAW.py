from rdflib import Graph, Namespace

# Laden
g = Graph()
g.parse("MusicHistoryGraph_TwelveToneMusic_Complete.ttl", format="ttl")

mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
schema = Namespace("https://schema.org/")

query = """
CONSTRUCT {
  ?composer frbr:creatorOf ?work .
  ?work a ?workType .
}
WHERE {
  VALUES ?composer { 
    mhg:AlbanBerg 
    mhg:ArnoldSchoenberg 
    mhg:AntonWebern 
  }
  ?composer a mhg:composer .
  OPTIONAL { ?composer frbr:creatorOf ?work . }
  OPTIONAL { ?work a ?workType . }
}
"""

subgraph = g.query(query).graph

# Prefixe hinzufügen
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

# Speichern
print(f"Triples im Subgraph: {len(subgraph)}")

subgraph.serialize("composer_ABASAW.ttl", format="turtle")
print("Subgraph gespeichert als composer_ABASAW.ttl")
