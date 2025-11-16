import json
import re
from datetime import datetime

def parse_ttl_block(block):
    """Parst einen TTL-Block und extrahiert die relevanten Informationen."""
    data = {
        'subject': None,
        'name': None,
        'sameAs': [],
        'birthDate': None,
        'birthPlace': None,
        'deathDate': None,
        'deathPlace': None,
        'raw_lines': block.split('\n'),
        'has_birthDate': False,
        'has_birthPlace': False,
        'has_deathDate': False,
        'has_deathPlace': False,
        'has_sameAs': False
    }
    
    # Subjekt extrahieren (z.B. mhg:TheodorWiesengrundAdorno)
    subject_match = re.search(r'^(mhg:\w+)\s+a', block)
    if subject_match:
        data['subject'] = subject_match.group(1)
    
    # Name extrahieren
    name_match = re.search(r'schema:name\s+"([^"]+)"', block)
    if name_match:
        data['name'] = name_match.group(1)
    
    # sameAs Links extrahieren und prüfen ob vorhanden
    sameas_matches = re.findall(r'schema:sameAs\s+<([^>]+)>', block)
    data['sameAs'] = sameas_matches
    data['has_sameAs'] = len(sameas_matches) > 0
    
    # Geburtsdatum extrahieren und prüfen ob vorhanden
    birthdate_match = re.search(r'schema:birthDate\s+"([^"]+)"\^\^xsd:date', block)
    if birthdate_match:
        data['birthDate'] = birthdate_match.group(1)
        data['has_birthDate'] = True
    
    # Geburtsort extrahieren und prüfen ob vorhanden
    birthplace_match = re.search(r'schema:birthPlace\s+<([^>]+)>', block)
    if birthplace_match:
        data['birthPlace'] = birthplace_match.group(1)
        data['has_birthPlace'] = True
    
    # Sterbedatum extrahieren und prüfen ob vorhanden
    deathdate_match = re.search(r'schema:deathDate\s+"([^"]+)"\^\^xsd:date', block)
    if deathdate_match:
        data['deathDate'] = deathdate_match.group(1)
        data['has_deathDate'] = True
    
    # Sterbeort extrahieren und prüfen ob vorhanden
    deathplace_match = re.search(r'schema:deathPlace\s+<([^>]+)>', block)
    if deathplace_match:
        data['deathPlace'] = deathplace_match.group(1)
        data['has_deathPlace'] = True
    
    return data

def convert_ttl_name_to_json_format(ttl_name):
    """Konvertiert TTL-Name 'Nachname, Vorname' zu JSON-Format 'Vorname Nachname'"""
    if ',' in ttl_name:
        parts = ttl_name.split(',', 1)
        return f"{parts[1].strip()} {parts[0].strip()}"
    return ttl_name

def format_date_for_ttl(json_date):
    """Formatiert JSON-Datum für TTL (entfernt Zeitanteil und fügt Datentyp hinzu)"""
    if json_date and 'T' in json_date:
        return json_date.split('T')[0] + '"^^xsd:date'
    return json_date

def update_ttl_block(block_data, json_entry):
    """Aktualisiert einen TTL-Block basierend auf JSON-Daten - vereinfachte und robuste Version"""
    changes = []
    lines = block_data['raw_lines'].copy()
    
    # Phase 1: Entferne alle vorhandenen Properties, die wir ersetzen wollen
    properties_to_remove = ['schema:birthDate', 'schema:birthPlace', 'schema:deathDate', 'schema:deathPlace', 'schema:sameAs']
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Überspringe Kommentare
        if stripped.startswith('#'):
            cleaned_lines.append(line)
            i += 1
            continue
            
        # Prüfe ob diese Zeile eine zu entfernende Property enthält
        remove_line = False
        for prop in properties_to_remove:
            if prop in stripped:
                # Wenn es sich um eine sameAs-Liste handelt, behalte sie aber merke sie für später
                if prop == 'schema:sameAs' and not stripped.startswith('schema:sameAs'):
                    # sameAs könnte über mehrere Zeilen gehen
                    pass
                else:
                    remove_line = True
                    # Wenn es eine ORIGINAL-Kommentarzeile ist, behalte den Kommentar
                    if 'ORIGINAL:' in line:
                        cleaned_lines.append(line)
                    else:
                        changes.append(f"Removed existing {prop}")
                    break
        
        if not remove_line:
            cleaned_lines.append(line)
        i += 1
    
    lines = cleaned_lines
    
    # Phase 2: Füge alle Properties in der richtigen Reihenfolge hinzu
    new_properties = []
    
    # sameAs - immer hinzufügen
    if json_entry.get('person'):
        # Sammle alle existing sameAs Links aus dem Block
        existing_sameas = block_data['sameAs'].copy()
        if json_entry['person'] not in existing_sameas:
            existing_sameas.append(json_entry['person'])
        
        if existing_sameas:
            sameas_lines = ['    schema:sameAs']
            for i, sameas in enumerate(existing_sameas):
                if i == 0:
                    sameas_lines.append(f'        <{sameas}>')
                else:
                    sameas_lines.append(f'        , <{sameas}>')
            sameas_lines[-1] = sameas_lines[-1] + ' ;'
            new_properties.append(('\n'.join(sameas_lines), 'sameAs'))
            changes.append(f"Added/updated sameAs with {len(existing_sameas)} links")
    
    # birthDate
    if json_entry.get('birthDate'):
        formatted_date = format_date_for_ttl(json_entry['birthDate'])
        if block_data.get('birthDate') and block_data['birthDate'] != formatted_date.replace('"^^xsd:date', ''):
            new_properties.append((f'    # ORIGINAL: schema:birthDate "{block_data["birthDate"]}"^^xsd:date ;\n    schema:birthDate "{formatted_date}" ;', 'birthDate'))
            changes.append(f"Updated birthDate from {block_data['birthDate']} to {formatted_date}")
        else:
            new_properties.append((f'    schema:birthDate "{formatted_date}" ;', 'birthDate'))
            changes.append(f"Added birthDate: {formatted_date}")
    
    # birthPlace
    if json_entry.get('birthPlace'):
        if block_data.get('birthPlace') and block_data['birthPlace'] != json_entry['birthPlace']:
            new_properties.append((f'    # ORIGINAL: schema:birthPlace <{block_data["birthPlace"]}> ;\n    schema:birthPlace <{json_entry["birthPlace"]}> ;', 'birthPlace'))
            changes.append(f"Updated birthPlace from {block_data['birthPlace']} to {json_entry['birthPlace']}")
        else:
            new_properties.append((f'    schema:birthPlace <{json_entry["birthPlace"]}> ;', 'birthPlace'))
            changes.append(f"Added birthPlace: {json_entry['birthPlace']}")
    
    # deathDate
    if json_entry.get('deathDate'):
        formatted_date = format_date_for_ttl(json_entry['deathDate'])
        if block_data.get('deathDate') and block_data['deathDate'] != formatted_date.replace('"^^xsd:date', ''):
            new_properties.append((f'    # ORIGINAL: schema:deathDate "{block_data["deathDate"]}"^^xsd:date ;\n    schema:deathDate "{formatted_date}" ;', 'deathDate'))
            changes.append(f"Updated deathDate from {block_data['deathDate']} to {formatted_date}")
        else:
            new_properties.append((f'    schema:deathDate "{formatted_date}" ;', 'deathDate'))
            changes.append(f"Added deathDate: {formatted_date}")
    
    # deathPlace
    if json_entry.get('deathPlace'):
        if block_data.get('deathPlace') and block_data['deathPlace'] != json_entry['deathPlace']:
            new_properties.append((f'    # ORIGINAL: schema:deathPlace <{block_data["deathPlace"]}> ;\n    schema:deathPlace <{json_entry["deathPlace"]}> ;', 'deathPlace'))
            changes.append(f"Updated deathPlace from {block_data['deathPlace']} to {json_entry['deathPlace']}")
        else:
            new_properties.append((f'    schema:deathPlace <{json_entry["deathPlace"]}> ;', 'deathPlace'))
            changes.append(f"Added deathPlace: {json_entry['deathPlace']}")
    
    # Phase 3: Finde die Einfügeposition nach schema:name
    insert_position = -1
    for i, line in enumerate(lines):
        if 'schema:name' in line and not line.strip().startswith('#'):
            insert_position = i + 1
            break
    
    if insert_position == -1:
        # Fallback: Füge vor dem schließenden Punkt ein
        for i, line in enumerate(lines):
            if line.strip() == '.':
                insert_position = i
                break
        if insert_position == -1:
            insert_position = len(lines)
    
    # Füge neue Properties in umgekehrter Reihenfolge ein (damit die Reihenfolge stimmt)
    for prop_content, prop_type in reversed(new_properties):
        lines.insert(insert_position, prop_content)
    
    # Phase 4: Korrigiere die Zeichensetzung
    # Entferne alle Punkte und Semikolons am Ende und setze sie korrekt
    for i in range(len(lines)):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            continue
            
        # Entferne falsche Zeichensetzung am Ende
        line = line.rstrip()
        if line.endswith(' .') or line.endswith(' ;') or line.endswith(' .;'):
            line = line[:-2].rstrip()
        
        lines[i] = line
    
    # Setze korrekte Zeichensetzung
    for i in range(len(lines)):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped or stripped.startswith('#'):
            continue
            
        # Wenn es die letzte Property-Zeile ist
        if i == len(lines) - 1 or (i < len(lines) - 1 and lines[i + 1].strip() == ''):
            if not line.endswith('.'):
                lines[i] = line + ' .'
        else:
            # Wenn es eine normale Property-Zeile ist
            next_line = lines[i + 1].strip() if i < len(lines) - 1 else ''
            if next_line and not next_line.startswith('#') and not line.endswith(',') and not line.endswith(';'):
                lines[i] = line + ' ;'
    
    return '\n'.join(lines), changes

def main():
    # Lade JSON-Daten
    with open('query_Wikidata.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Lade TTL-Datei
    with open('composers_interim.ttl', 'r', encoding='utf-8') as f:
        ttl_content = f.read()
    
    # Erstelle Mapping von JSON-Namen zu Einträgen
    json_mapping = {}
    for entry in json_data:
        json_mapping[entry['personLabel']] = entry
    
    # Zerlege TTL in Blöcke
    ttl_blocks = re.split(r'\n\n+', ttl_content)
    updated_blocks = []
    total_changes = []
    
    print("Überprüfe und aktualisiere TTL-Einträge...")
    print("=" * 60)
    
    for block in ttl_blocks:
        if not block.strip() or not block.startswith('mhg:'):
            updated_blocks.append(block)
            continue
        
        block_data = parse_ttl_block(block)
        
        if not block_data['name']:
            updated_blocks.append(block)
            continue
        
        # Konvertiere TTL-Name zu JSON-Format
        json_format_name = convert_ttl_name_to_json_format(block_data['name'])
        
        # Prüfe ob ein Match in JSON existiert
        if json_format_name in json_mapping:
            json_entry = json_mapping[json_format_name]
            
            print(f"\nGefunden: {block_data['subject']}")
            print(f"  Match: '{block_data['name']}' -> '{json_format_name}'")
            
            # Zeige vorhandene und fehlende Properties an
            existing = []
            missing = []
            
            if block_data['has_sameAs']:
                existing.append("sameAs")
            elif json_entry.get('person'):
                missing.append("sameAs")
                
            if block_data['has_birthDate']:
                existing.append("birthDate")
            elif json_entry.get('birthDate'):
                missing.append("birthDate")
                
            if block_data['has_birthPlace']:
                existing.append("birthPlace")
            elif json_entry.get('birthPlace'):
                missing.append("birthPlace")
                
            if block_data['has_deathDate']:
                existing.append("deathDate")
            elif json_entry.get('deathDate'):
                missing.append("deathDate")
                
            if block_data['has_deathPlace']:
                existing.append("deathPlace")
            elif json_entry.get('deathPlace'):
                missing.append("deathPlace")
            
            if existing:
                print(f"  Vorhanden: {', '.join(existing)}")
            if missing:
                print(f"  Fehlend: {', '.join(missing)}")
            
            # Aktualisiere den Block
            updated_block, changes = update_ttl_block(block_data, json_entry)
            
            if changes:
                print(f"  Änderungen:")
                for change in changes:
                    print(f"    - {change}")
                total_changes.extend([(block_data['subject'], change) for change in changes])
            else:
                print(f"  ✓ Keine Änderungen notwendig")
            
            updated_blocks.append(updated_block)
        else:
            updated_blocks.append(block)
            print(f"\nKein Match: {block_data['subject']} ('{block_data['name']}')")
    
    # Schreibe aktualisierte TTL-Datei
    with open('composers_updated.ttl', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(updated_blocks))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG:")
    print(f"Anzahl durchgehörter Blöcke: {len(ttl_blocks)}")
    print(f"Anzahl durchgeführter Änderungen: {len(total_changes)}")
    
    if total_changes:
        print("\nDetails der Änderungen:")
        change_types = {}
        for subject, change in total_changes:
            change_type = change.split(':')[0] if ':' in change else change.split()[0]
            change_types[change_type] = change_types.get(change_type, 0) + 1
            print(f"  {subject}: {change}")
        
        print("\nZusammenfassung nach Typ:")
        for change_type, count in change_types.items():
            print(f"  {change_type}: {count}")

if __name__ == "__main__":
    main()