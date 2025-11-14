from rdflib import Graph, Namespace

# Laden
g = Graph()
g.parse("MusicHistoryGraph_TwelveToneMusic_Complete.ttl", format="ttl")

mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
frbr = Namespace("http://purl.org/vocab/frbr/core/")
schema = Namespace("https://schema.org/")

query = """
PREFIX mhg: <http://music-history-graph.ch/twelve-tone-onto#>
PREFIX frbr: <http://purl.org/vocab/frbr/core/>
PREFIX schema: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

CONSTRUCT {
  ?composer a mhg:composer ;
            frbr:creatorOf ?work .
  ?work a ?workType ;
        frbr:hasCreationDate ?date .
}
WHERE {
  ?composer a mhg:composer .
  ?composer frbr:creatorOf ?work .
  OPTIONAL { ?work a ?workType . }
  OPTIONAL { ?work frbr:hasCreationDate ?date . }
  FILTER (
    bound(?date) &&
    xsd:integer(SUBSTR(STR(?date), 1, 4)) < 1960
  )
}
"""

subgraph = g.query(query).graph

# Prefixe hinzufügen
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

# Speichern
print(f"Triples im Subgraph: {len(subgraph)}")

subgraph.serialize("composer_work_before1960.ttl", format="turtle")
print("Subgraph gespeichert als composer_work_before1960.ttl")
