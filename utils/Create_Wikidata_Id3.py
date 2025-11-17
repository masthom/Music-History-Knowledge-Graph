import requests
import time
import json

API_URL = "https://www.wikidata.org/w/api.php"

# -------------------------------------------------------
# Funktion: Suche nach Q-ID für einen Namen
# -------------------------------------------------------
def get_qid_for_name(name):
    headers = {
        'User-Agent': 'MusicHistoryResearch/1.0 (https://example.com; thoma@example.com)',
        'Accept': 'application/json',
    }
    
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "format": "json",
        "limit": 10
    }
    
    try:
        r = requests.get(API_URL, params=params, headers=headers, timeout=30)
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 403:
            print("Zugriff verweigert - möglicherweise Rate Limiting")
            return None
        elif r.status_code == 429:
            print("Zu viele Anfragen - warte länger")
            time.sleep(10)
            return None
            
        r.raise_for_status()
        data = r.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Abfrage für '{name}': {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Parse Fehler für '{name}': {e}")
        print(f"Response text: {r.text[:200]}...")
        return None

    if "search" not in data or len(data["search"]) == 0:
        print(f"Keine Ergebnisse gefunden für: {name}")
        return None

    candidates = data["search"]
    print(f"  Gefunden: {len(candidates)} Kandidaten")

    # 1. Zuerst menschliche Entitäten auswählen (Q5)
    for c in candidates:
        if "description" in c and "human" in c["description"].lower():
            print(f"  ✓ Human gefunden: {c['id']} - {c['label']}")
            return c["id"]

    # 2. Falls kein "human", nimm besten Treffer
    if candidates:
        print(f"  → Ersten Treffer genommen: {candidates[0]['id']} - {candidates[0]['label']}")
        return candidates[0]["id"]
    
    return None

# -------------------------------------------------------
# Alternative Funktion mit SPARQL (falls API nicht funktioniert)
# -------------------------------------------------------
def get_qid_via_sparql(name):
    """Alternative Methode über SPARQL Endpoint"""
    query = """
    SELECT ?item WHERE {
      ?item ?label "%s"@en.
      ?item wdt:P31 wd:Q5.  # Ist eine menschliche Entität
    }
    LIMIT 1
    """ % name.replace('"', '\\"')
    
    url = "https://query.wikidata.org/sparql"
    headers = {
        'User-Agent': 'MusicHistoryResearch/1.0',
        'Accept': 'application/json'
    }
    
    try:
        r = requests.get(url, params={'format': 'json', 'query': query}, 
                        headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data['results']['bindings']:
                qid = data['results']['bindings'][0]['item']['value'].split('/')[-1]
                print(f"  ✓ Via SPARQL gefunden: {qid}")
                return qid
    except Exception as e:
        print(f"  SPARQL Fehler: {e}")
    
    return None

# -------------------------------------------------------
# NAMENSLISTE 
# -------------------------------------------------------
names = [
      "Bernd Alois Zimmermann",
    "Bernhard Lang",
    "Bill Dobbins",
    "Bill Evans",
    "Brian Ferneyhough",
    "Bruno Maderna",
    "Béla Bartók",
    "Carl Ruggles",
    "Charles Ives",
    "Charles Wuorinen",
    "Chen Yi",
    "Christine Badger",
    "Claudio Santoro",
    "David Baker",
    "David Diamond",
    "David Dzubay",
    "David Lewin",
    "David Shire",
    "Dika Newlin",
    "Dimitri Papageorgiou",
    "Dmitri Shostakovich",
    "Dominick Argento",
    "Donald Martino",
    "Edison Denisov",
    "Eduard Steuermann",
    "Elisabeth Lutyens",
    "Elliott Carter",
    "Eric Ross",
    "Erich Itor Kahn",
    "Erich Schmid",
    "Erich Urbanner",
    "Ernst Christian Rinner",
    "Ernst Krenek",
    "Erwin Stein",
    "Felicitas Kukuck",
    "Florian Geßler",
    "Frank Martin",
    "Frank Zappa",
    "Franz Liszt",
    "Fritz Heinrich Klein",
    "George Perle",
    "George Rochberg",
    "George Walker",
    "Georgia Kalodiki",
    "Gerhard Nierhaus",
    "Gordon Crosse",
    "Gunther Schuller",
    "György Kurtág",
    "György Ligeti",
    "Hale Smith",
    "Hanns Eisler",
    "Hanns Jelinek",
    "Hans Erich Apostel",
    "Hans Florey",
    "Helmut Eder",
    "Helmut Lachenmann",
    "Henri Pousseur",
    "Henrik Sande",
    "Herbert Eimert",
    "Herman Heiß",
    "Hermann Markus Preßl",
    "Humphrey Searle",
    "Igor Stravinsky",
    "Irving Fine",
    "Isang Yun",
    "Ivan Eröd",
    "Jeff Nichols",
    "Jian-Zhong Wang",
    "Jin-Min Zhou",
    "Johann Nepomuk David",
    "Johann Sebastian Bach",
    "Johann Sengstschmid",
    "John Cage",
    "John Coltrane",
    "Joonas Kokkonen",
    "Josef Matthias Hauer",
    "Josef Mittendorfer",
    "Josef Rufer",
    "Joseph Schwantner",
    "Juan Carlos",
    "Karel Goeyvaerts",
    "Karel Husa",
    "Karl Amadeus Hartmann",
    "Karl Schiske",
    "Karlheinz Stockhausen",
    "Klaus Huber",
    "Klaus Lang",
    "Kurt Atterberg",
    "Leopold Spinner",
    "Lou Harrison",
    "Louise Talma",
    "Luciano Berio",
    "Ludwig Zenk",
    "Luigi Dallapiccola",
    "Luigi Nono",
    "Mark Gotham",
    "Maximilian Hendler",
    "Michael Gielen",
    "Michel Fano",
    "Milton Babbitt",
    "Mátyás Seiber",
    "Nicholas Slonimsky",
    "Nikos Skalkotas",
    "Norma Beecroft",
    "Olivier Messiaen",
    "Olly Wilson",
    "Orestis Toufektsis",
    "Othmar Steinbauer",
    "Paul Dessau",
    "Paul Hindemith",
    "Paul von Klenau",
    "Peter Lackner",
    "Peter Maxwell Davies",
    "Peter Michael Hamel",
    "Peter Tranchell",
    "Peter Westergaard",
    "Pierre Boulez",
    "Rainer Bischof",
    "Ralph Shapey",
    "René Leibowitz",
    "Richard Rodney Bennett",
    "Richard Strauss",
    "Robert Moevs",
    "Robert Morris",
    "Robert Schollum",
    "Roberto Gerhard",
    "Roger Reynolds",
    "Roger Sessions",
    "Roque Cordero",
    "Ross Lee Finney",
    "Samuel Barber",
    "Shi-Lin Lu",
    "Sigrid Riegebauer",
    "Stefan Wolpe",
    "Thea Musgrave",
    "Theodor W. Adorno",
    "Thomas Schreiner",
    "Ursula Mamlok",
    "Vivian Fine",
    "Walter Piston",
    "Wilfried Zillig",
    "William Walton",
    "Witold Lutosławski",
    "Wolfgang Fortner",
    "Xi-Lin Wang",
    "Yannis Papaioannou",
    "Yen Lu",
    "York Höller",
    "Zhong-Rong Luo"
]

# -------------------------------------------------------
# Verarbeitung mit verbesserter Fehlerbehandlung
# -------------------------------------------------------
results = {}
failed_names = []

print(f"Starte Suche für {len(names)} Namen...")
print("=" * 50)

for i, name in enumerate(names, 1):
    print(f"\n[{i}/{len(names)}] Suche: {name}")
    
    # Hauptmethode über API
    qid = get_qid_for_name(name)
    
    # Falls fehlgeschlagen, versuche SPARQL
    if not qid:
        print(f"  Versuche SPARQL für: {name}")
        qid = get_qid_via_sparql(name)
    
    if qid:
        results[name] = qid
        print(f"  ✅ ERFOLG: {name} → {qid}")
    else:
        results[name] = None
        failed_names.append(name)
        print(f"  ❌ FEHLGESCHLAGEN: {name}")
    
    # Längere Pause zwischen Anfragen
    time.sleep(2)  # 2 Sekunden Pause
    
    # Nach 20 Anfragen eine längere Pause
    if i % 20 == 0:
        print("\n💤 Lange Pause wegen Rate Limiting...")
        time.sleep(30)

# -------------------------------------------------------
# Ausgabe der Ergebnisse
# -------------------------------------------------------
print("\n" + "=" * 50)
print("ZUSAMMENFASSUNG:")
print(f"Erfolgreich gefunden: {len([v for v in results.values() if v is not None])}")
print(f"Nicht gefunden: {len(failed_names)}")

if failed_names:
    print("\nNicht gefundene Namen:")
    for name in failed_names:
        print(f"  - {name}")

# SPARQL VALUES Format
print("\nVALUES ?person {")
for name, qid in results.items():
    if qid is None:
        print(f"  # NICHT GEFUNDEN: {name}")
    else:
        print(f"  wd:{qid}    # {name}")
print("}")

# Zusätzlich: CSV-Format für bessere Nachverfolgung
print("\n# CSV Format:")
print("Name,QID")
for name, qid in results.items():
    qid_str = qid if qid else "NOT_FOUND"
    print(f"{name},{qid_str}")