import requests
import time

API_URL = "https://www.wikidata.org/w/api.php"

# -------------------------------------------------------
# Funktion: Suche nach Q-ID für einen Namen
# -------------------------------------------------------
def get_qid_for_name(name):
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "format": "json",
        "limit": 10
    }
    r = requests.get(API_URL, params=params)
    data = r.json()

    if "search" not in data or len(data["search"]) == 0:
        return None

    candidates = data["search"]

    # 1. Zuerst Q5 auswählen, falls vorhanden (Menschen)
    for c in candidates:
        if "description" in c and "human" in c["description"].lower():
            return c["id"]

    # 2. Falls kein "human", nimm besten Treffer
    return candidates[0]["id"]


# -------------------------------------------------------
# NAMENSLISTE HIER EINTRAGEN
# (deine Liste kann beliebig lang sein)
# -------------------------------------------------------
names = [
    "Aaron Copland"
  "Adolph Weiss"
  "Alban Berg"
  "Alberto Ginastera"
  "Alexander Goehr"
  "Alfred Schnittke"
  "Andrei Volkonsky"
  "Andrzej Panufnik"
  "Anton Webern"
  "Antony Payne"
  "Arnold Schoenberg"
  "Arrigo Barnabé"
  "Arthur Berger"
  "Arvo Pärt"
  "Bao-Shu Li"
  "Barbara Pentland"
  "Ben Johnston"
  "Ben Weber"
  "Benjamin Britten"
  "Benjamin Frankel"
  "Bernd Alois Zimmermann"
  "Bernhard Lang"
  "Bill Dobbins"
  "Bill Evans"
  "Brian Ferneyhough"
  "Bruno Maderna"
  "Béla Bartók"
  "Carl Ruggles"
  "Charles Ives"
  "Charles Wuorinen"
  "Chen Yi"
  "Christine Badger"
  "Claudio Santoro"
  "David Baker"
  "David Diamond"
  "David Dzubay"
  "David Lewin"
  "David Shire"
  "Dika Newlin"
  "Dimitri Papageorgiou"
  "Dmitri Shostakovich"
  "Dominick Argento"
  "Donald Martino"
  "Edison Denisov"
  "Eduard Steuermann"
  "Elisabeth Lutyens"
  "Elliott Carter"
  "Eric Ross"
  "Erich Itor Kahn"
  "Erich Schmid"
  "Erich Urbanner"
  "Ernst Christian Rinner"
  "Ernst Krenek"
  "Erwin Stein"
  "Felicitas Kukuck"
  "Florian Geßler"
  "Frank Martin"
  "Frank Zappa"
  "Franz Liszt"
  "Fritz Heinrich Klein"
  "George Perle"
  "George Rochberg"
  "George Walker"
  "Georgia Kalodiki"
  "Gerhard Nierhaus"
  "Gordon Crosse"
  "Gunther Schuller"
  "György Kurtág"
  "György Ligeti"
  "Hale Smith"
  "Hanns Eisler"
  "Hanns Jelinek"
  "Hans Erich Apostel"
  "Hans Florey"
  "Helmut Eder"
  "Helmut Lachenmann"
  "Henri Pousseur"
  "Henrik Sande"
  "Herbert Eimert"
  "Herman Heiß"
  "Hermann Markus Preßl"
  "Humphrey Searle"
  "Igor Stravinsky"
  "Irving Fine"
  "Isang Yun"
  "Ivan Eröd"
  "Jeff Nichols"
  "Jian-Zhong Wang"
  "Jin-Min Zhou"
  "Johann Nepomuk David"
  "Johann Sebastian Bach"
  "Johann Sengstschmid"
  "John Cage"
  "John Coltrane"
  "Joonas Kokkonen"
  "Josef Matthias Hauer"
  "Josef Mittendorfer"
  "Josef Rufer"
  "Joseph Schwantner"
  "Juan Carlos"
  "Karel Goeyvaerts"
  "Karel Husa"
  "Karl Amadeus Hartmann"
  "Karl Schiske"
  "Karlheinz Stockhausen"
  "Klaus Huber"
  "Klaus Lang"
  "Kurt Atterberg"
  "Leopold Spinner"
  "Lou Harrison"
  "Louise Talma"
  "Luciano Berio"
  "Ludwig Zenk"
  "Luigi Dallapiccola"
  "Luigi Nono"
  "Mark Gotham"
  "Maximilian Hendler"
  "Michael Gielen"
  "Michel Fano"
  "Milton Babbitt"
  "Mátyás Seiber"
  "Nicholas Slonimsky"
  "Nikos Skalkotas"
  "Norma Beecroft"
  "Olivier Messiaen"
  "Olly Wilson"
  "Orestis Toufektsis"
  "Othmar Steinbauer"
  "Paul Dessau"
  "Paul Hindemith"
  "Paul von Klenau"
  "Peter Lackner"
  "Peter Maxwell Davies"
  "Peter Michael Hamel"
  "Peter Tranchell"
  "Peter Westergaard"
  "Pierre Boulez"
  "Rainer Bischof"
  "Ralph Shapey"
  "René Leibowitz"
  "Richard Rodney Bennett"
  "Richard Strauss"
  "Robert Moevs"
  "Robert Morris"
  "Robert Schollum"
  "Roberto Gerhard"
  "Roger Reynolds"
  "Roger Sessions"
  "Roque Cordero"
  "Ross Lee Finney"
  "Samuel Barber"
  "Shi-Lin Lu"
  "Sigrid Riegebauer"
  "Stefan Wolpe"
  "Thea Musgrave"
  "Theodor W. Adorno"
  "Thomas Schreiner"
  "Ursula Mamlok"
  "Vivian Fine"
  "Walter Piston"
  "Wilfried Zillig"
  "William Walton"
  "Witold Lutosławski"
  "Wolfgang Fortner"
  "Xi-Lin Wang"
  "Yannis Papaioannou"
  "Yen Lu"
  "York Höller"
  "Zhong-Rong Luo"
    # ... hier deine komplette 200er-Liste einfügen ...
]


# -------------------------------------------------------
# Verarbeitung
# -------------------------------------------------------
results = {}
for name in names:
    print(f"Suche: {name}")
    qid = get_qid_for_name(name)
    results[name] = qid
    time.sleep(0.1)  # freundlich zur API

# -------------------------------------------------------
# Ausgabe der SPARQL-VALUES-Liste
# -------------------------------------------------------
print("\nVALUES ?person {")
for name, qid in results.items():
    if qid is None:
        print(f"  # NICHT GEFUNDEN: {name}")
    else:
        print(f"  wd:{qid}    # {name}")
print("}")
