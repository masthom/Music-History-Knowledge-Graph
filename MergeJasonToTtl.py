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
        'raw_lines': block.split('\n')
    }
    
    # Subjekt extrahieren (z.B. mhg:TheodorWiesengrundAdorno)
    subject_match = re.search(r'^(mhg:\w+)\s+a', block)
    if subject_match:
        data['subject'] = subject_match.group(1)
    
    # Name extrahieren
    name_match = re.search(r'schema:name\s+"([^"]+)"', block)
    if name_match:
        data['name'] = name_match.group(1)
    
    # sameAs Links extrahieren
    sameas_matches = re.findall(r'schema:sameAs\s+<([^>]+)>', block)
    data['sameAs'] = sameas_matches
    
    # Geburtsdatum extrahieren
    birthdate_match = re.search(r'schema:birthDate\s+"([^"]+)"', block)
    if birthdate_match:
        data['birthDate'] = birthdate_match.group(1)
    
    # Geburtsort extrahieren
    birthplace_match = re.search(r'schema:birthPlace\s+<([^>]+)>', block)
    if birthplace_match:
        data['birthPlace'] = birthplace_match.group(1)
    
    # Sterbedatum extrahieren
    deathdate_match = re.search(r'schema:deathDate\s+"([^"]+)"', block)
    if deathdate_match:
        data['deathDate'] = deathdate_match.group(1)
    
    # Sterbeort extrahieren
    deathplace_match = re.search(r'schema:deathPlace\s+<([^>]+)>', block)
    if deathplace_match:
        data['deathPlace'] = deathplace_match.group(1)
    
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
    """Aktualisiert einen TTL-Block basierend auf JSON-Daten"""
    updated_lines = []
    changes = []
    
    for line in block_data['raw_lines']:
        original_line = line
        
        # Überprüfe und aktualisiere sameAs
        if 'schema:sameAs' in line and json_entry['person'] not in block_data['sameAs']:
            # Füge Wikidata-QID zu sameAs hinzu
            if line.strip().endswith(';') or line.strip().endswith('.'):
                line = line.rstrip('; .') + f',\n        <{json_entry["person"]}> ;'
            changes.append(f"Added sameAs: {json_entry['person']}")
        
        # Überprüfe und aktualisiere birthDate
        elif 'schema:birthDate' in line and json_entry.get('birthDate'):
            json_date = format_date_for_ttl(json_entry['birthDate'])
            if block_data['birthDate']:
                if block_data['birthDate'] != json_date.replace('"^^xsd:date', ''):
                    # Kommentiere alten Wert aus und füge neuen hinzu
                    old_value = re.search(r'"([^"]+)"', line).group(1) if '"' in line else 'unknown'
                    line = f"    # ORIGINAL: {original_line.strip()}\n    schema:birthDate \"{json_date}\" ;"
                    changes.append(f"Updated birthDate from {old_value} to {json_date}")
            else:
                # Füge neuen birthDate hinzu
                if line.strip().endswith('schema:name'):
                    line = line + f'\n    schema:birthDate "{json_date}" ;'
                changes.append(f"Added birthDate: {json_date}")
        
        # Überprüfe und aktualisiere birthPlace
        elif 'schema:birthPlace' in line and json_entry.get('birthPlace'):
            if block_data['birthPlace']:
                if block_data['birthPlace'] != json_entry['birthPlace']:
                    old_value = block_data['birthPlace']
                    line = f"    # ORIGINAL: {original_line.strip()}\n    schema:birthPlace <{json_entry['birthPlace']}> ;"
                    changes.append(f"Updated birthPlace from {old_value} to {json_entry['birthPlace']}")
            else:
                if line.strip().endswith('schema:name') or ('schema:birthDate' in ''.join(updated_lines[-2:]) if updated_lines else False):
                    line = line + f'\n    schema:birthPlace <{json_entry["birthPlace"]}> ;'
                changes.append(f"Added birthPlace: {json_entry['birthPlace']}")
        
        # Überprüfe und aktualisiere deathDate
        elif 'schema:deathDate' in line and json_entry.get('deathDate'):
            json_date = format_date_for_ttl(json_entry['deathDate'])
            if block_data['deathDate']:
                if block_data['deathDate'] != json_date.replace('"^^xsd:date', ''):
                    old_value = re.search(r'"([^"]+)"', line).group(1) if '"' in line else 'unknown'
                    line = f"    # ORIGINAL: {original_line.strip()}\n    schema:deathDate \"{json_date}\" ;"
                    changes.append(f"Updated deathDate from {old_value} to {json_date}")
            else:
                if line.strip().endswith('schema:name') or any(x in ''.join(updated_lines[-2:]) for x in ['schema:birth', 'frbr:creatorOf'] if updated_lines):
                    line = line + f'\n    schema:deathDate "{json_date}" ;'
                changes.append(f"Added deathDate: {json_date}")
        
        # Überprüfe und aktualisiere deathPlace
        elif 'schema:deathPlace' in line and json_entry.get('deathPlace'):
            if block_data['deathPlace']:
                if block_data['deathPlace'] != json_entry['deathPlace']:
                    old_value = block_data['deathPlace']
                    line = f"    # ORIGINAL: {original_line.strip()}\n    schema:deathPlace <{json_entry['deathPlace']}> ;"
                    changes.append(f"Updated deathPlace from {old_value} to {json_entry['deathPlace']}")
            else:
                if line.strip().endswith('schema:name') or any(x in ''.join(updated_lines[-2:]) for x in ['schema:deathDate', 'schema:birth'] if updated_lines):
                    line = line + f'\n    schema:deathPlace <{json_entry["deathPlace"]}> ;'
                changes.append(f"Added deathPlace: {json_entry['deathPlace']}")
        
        updated_lines.append(line)
    
    # Füge fehlende Eigenschaften am Ende hinzu, falls nicht vorhanden
    final_block = '\n'.join(updated_lines)
    
    # Füge sameAs hinzu falls komplett fehlend
    if not block_data['sameAs'] and json_entry.get('person'):
        if 'schema:sameAs' not in final_block:
            # Finde die letzte Property-Zeile vor dem Punkt
            lines = final_block.split('\n')
            for i, line in enumerate(lines):
                if line.strip().endswith(';') and not any(prop in line for prop in ['sameAs', 'birthDate', 'deathDate', 'birthPlace', 'deathPlace']):
                    # Füge sameAs nach dieser Zeile ein
                    lines.insert(i + 1, f'    schema:sameAs <{json_entry["person"]}> ;')
                    changes.append(f"Added missing sameAs: {json_entry['person']}")
                    break
            final_block = '\n'.join(lines)
    
    return final_block, changes

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
    print(f"Anzahl durchgeführter Änderungen: {len(total_changes)}")
    
    if total_changes:
        print("\nDetails der Änderungen:")
        for subject, change in total_changes:
            print(f"  {subject}: {change}")

if __name__ == "__main__":
    main()