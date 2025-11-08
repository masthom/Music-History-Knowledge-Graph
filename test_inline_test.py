from rdflib import Graph

data = """@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix frbr: <http://purl.org/vocab/frbr/core/> .
@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

#################################################################
## ONTOLOGY (Fragment: TODO)
#################################################################

mhg:isoCountryCode rdfs:subPropertyOf dcterms:identifier ;
    rdfs:label "ISO 3166-1 alpha-3 country code"@en .
"""

g = Graph()
g.parse(data=data, format="turtle")
print("✅ Parsed OK, triples:", len(g))
