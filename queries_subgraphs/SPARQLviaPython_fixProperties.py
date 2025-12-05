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
  ?rf a mhg:rowForm ; 
        mhg:manifestedIn mhg:Stravinsky_Movements .
  ?rc a mhg:rowClass ;
        mhg:actualizedIn mhg:Stravinsky_Movements .
}
WHERE {
  ?rf a mhg:rowForm ; 
        mhg:manifestedIn mhg:Stravinsky_Movements .
  ?rc a mhg:rowClass ;
        mhg:actualizedIn mhg:Stravinsky_Movements .
}
"""

subgraph = g.query(query).graph

# Prefixe hinzufügen
subgraph.bind("mhg", mhg)
subgraph.bind("frbr", frbr)
subgraph.bind("schema", schema)

# Speichern
print(f"Triples im Subgraph: {len(subgraph)}")

subgraph.serialize("TestStravinsky.ttl", format="turtle")
print("Subgraph gespeichert")
