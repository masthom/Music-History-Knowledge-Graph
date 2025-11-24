from rdflib import Graph, Namespace

# Laden
g = Graph()
g.parse("MusicHistoryGraph_TwelveToneMusic_Complete.ttl", format="ttl")

mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
schema = Namespace("https://schema.org/")

query = """
PREFIX mhg: <http://music-history-graph.ch/twelve-tone-onto#>

CONSTRUCT {
  # Rotationsbeziehung
  ?X mhg:hasRotations ?Y .

  # alle weiteren Properties von X
  ?X ?p ?o .

  ?o ?pp ?oo .
}
WHERE {
  # finde alle X, die Rotationen haben
  ?X mhg:hasRotations ?Y .

  # finde alle anderen Properties von X
  ?X ?p ?o .
  ?o ?pp ?oo .
  
  # OPTIONAL: Wenn du keine Typen willst, diese Zeilen aktivieren:
  FILTER(?p != rdf:type)
  FILTER(?pp != rdf:type)
}

"""

subgraph = g.query(query).graph

# Prefixe hinzufügen
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

# Speichern
print(f"Triples im Subgraph: {len(subgraph)}")

subgraph.serialize("subgraph_rotations.ttl", format="turtle")
print("subgraph_rotations.ttl gespeichert")
