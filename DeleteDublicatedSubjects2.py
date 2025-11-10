from rdflib import Graph, Namespace, URIRef

# === Namespaces ===
mhg = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
dcterms = Namespace("http://purl.org/dc/terms/")

# === Dateien ===
input_file = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
output_file = "merged_rowclasses_grouped.ttl"

# === Graph laden ===
g = Graph()
g.parse(input_file, format="ttl")

# === alle rowForms gruppieren nach rowClass ===
rowform_groups = {}

for s, p, o in g.triples((None, mhg.hasRowClass, None)):
    row_class = str(o)
    if row_class not in rowform_groups:
        rowform_groups[row_class] = []
    rowform_groups[row_class].append(s)

# === manuell Turtle-Text erzeugen ===
with open(output_file, "w", encoding="utf-8") as f:
    f.write("@prefix mhg: <http://music-history-graph.ch/twelve-tone-onto#> .\n")
    f.write("@prefix dcterms: <http://purl.org/dc/terms/> .\n\n")

    for row_class, forms in rowform_groups.items():
        f.write(f"# --- RowClass: {row_class.split('#')[-1]} ---\n")
        for form in forms:
            f.write(f"mhg:{form.split('#')[-1]} ")
            preds = list(g.predicate_objects(subject=form))
            first = True
            for p, o in preds:
                # Kompakte Darstellung
                pred_name = p.split("#")[-1]
                if isinstance(o, URIRef):
                    obj_str = f"mhg:{o.split('#')[-1]}"
                elif o.startswith("http"):
                    obj_str = f"<{o}>"
                else:
                    obj_str = f"\"{o}\""

                if first:
                    f.write(f"a mhg:rowForm ;\n        ")
                    first = False
                f.write(f"mhg:{pred_name} {obj_str} ;\n        ")
            f.write(".\n\n")

print(f"Datei '{output_file}' wurde erstellt.")
