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
    birthdate_match = re.search(r'schema:birthDate\s+"([^"]+)"', block)
    if birthdate_match:
        data['birthDate'] = birthdate_match.group(1)
        data['has_birthDate'] = True
    
    # Geburtsort extrahieren und prüfen ob vorhanden
    birthplace_match = re.search(r'schema:birthPlace\s+<([^>]+)>', block)
    if birthplace_match:
        data['birthPlace'] = birthplace_match.group(1)
        data['has_birthPlace'] = True
    
    # Sterbedatum extrahieren und prüfen ob vorhanden
    deathdate_match = re.search(r'schema:deathDate\s+"([^"]+)"', block)
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

def find_insert_position(lines, subject):
    """Findet die beste Position zum Einfügen neuer Properties"""
    # Bevorzugte Positionen in Reihenfolge
    preferred_patterns = [
        r'schema:deathDate',
        r'schema:birthDate', 
        r'schema:name',
        r'frbr:creatorOf',
        r'mhg:composer'
    ]
    
    # Suche nach vorhandenen Properties
    for pattern in preferred_patterns:
        for i, line in enumerate(lines):
            if re.search(pattern, line) and not line.strip().startswith('#'):
                return i + 1
    
    # Falls keine passende Stelle gefunden, vor dem schließenden Punkt einfügen
    for i, line in enumerate(lines):
        if line.strip() == '.':
            return i
    
    return len(lines) - 1

def ensure_correct_punctuation(lines):
    """Stellt korrekte TTL-Zeichensetzung sicher"""
    if not lines:
        return lines
        
    # Finde alle nicht-Kommentar, nicht-leere Zeilen
    content_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            content_lines.append(i)
    
    if not content_lines:
        return lines
    
    result = lines.copy()
    
    # Alle Inhaltszeilen (außer der letzten) mit Semikolon beenden
    for i in content_lines[:-1]:
        line = result[i].rstrip()
        if not line.endswith(';') and not line.endswith(','):
            result[i] = line + ' ;'
    
    # Letzte Inhaltszeile mit Punkt beenden (nur wenn nicht schon vorhanden)
    last_idx = content_lines[-1]
    last_line = result[last_idx].rstrip()
    if not last_line.endswith('.'):
        # Entferne eventuelles Semikolon am Ende
        last_line = last_line.rstrip(';')
        result[last_idx] = last_line + ' .'
    
    return result

def add_missing_properties(block_data, json_entry, lines):
    """Fügt komplett fehlende Properties hinzu"""
    changes = []
    new_lines = lines.copy()
    
    # Prüfe welche Properties fehlen und in JSON vorhanden sind
    properties_to_add = []
    
    if not block_data['has_sameAs'] and json_entry.get('person'):
        properties_to_add.append(('sameAs', f'    schema:sameAs <{json_entry["person"]}>'))
        changes.append(f"Added missing sameAs: {json_entry['person']}")
    
    if not block_data['has_birthDate'] and json_entry.get('birthDate'):
        formatted_date = format_date_for_ttl(json_entry['birthDate'])
        properties_to_add.append(('birthDate', f'    schema:birthDate "{formatted_date}"'))
        changes.append(f"Added missing birthDate: {formatted_date}")
    
    if not block_data['has_birthPlace'] and json_entry.get('birthPlace'):
        properties_to_add.append(('birthPlace', f'    schema:birthPlace <{json_entry["birthPlace"]}>'))
        changes.append(f"Added missing birthPlace: {json_entry['birthPlace']}")
    
    if not block_data['has_deathDate'] and json_entry.get('deathDate'):
        formatted_date = format_date_for_ttl(json_entry['deathDate'])
        properties_to_add.append(('deathDate', f'    schema:deathDate "{formatted_date}"'))
        changes.append(f"Added missing deathDate: {formatted_date}")
    
    if not block_data['has_deathPlace'] and json_entry.get('deathPlace'):
        properties_to_add.append(('deathPlace', f'    schema:deathPlace <{json_entry["deathPlace"]}>'))
        changes.append(f"Added missing deathPlace: {json_entry['deathPlace']}")
    
    # Füge fehlende Properties an der richtigen Position ein
    if properties_to_add:
        insert_pos = find_insert_position(new_lines, block_data['subject'])
        
        # Sortiere Properties in empfohlener Reihenfolge
        property_order = ['birthDate', 'birthPlace', 'deathDate', 'deathPlace', 'sameAs']
        sorted_properties = sorted(properties_to_add, key=lambda x: property_order.index(x[0]) if x[0] in property_order else len(property_order))
        
        for prop_name, prop_line in reversed(sorted_properties):
            new_lines.insert(insert_pos, prop_line)
    
    return new_lines, changes

def update_ttl_block(block_data, json_entry):
    """Aktualisiert einen TTL-Block basierend auf JSON-Daten"""
    updated_lines = []
    changes = []
    
    # Phase 1: Vorhandene Properties aktualisieren und alle Zeilen durchgehen
    i = 0
    while i < len(block_data['raw_lines']):
        line = block_data['raw_lines'][i]
        stripped = line.strip()
        
        # Leere Zeilen und Kommentare direkt übernehmen
        if not stripped or stripped.startswith('#'):
            updated_lines.append(line)
            i += 1
            continue
            
        line_modified = False
        
        # Überprüfe und aktualisiere sameAs
        if 'schema:sameAs' in line and json_entry.get('person') and json_entry['person'] not in block_data['sameAs']:
            # Füge Wikidata-QID zu sameAs hinzu
            if stripped.endswith(';') or stripped.endswith('.'):
                # sameAs als Liste erweitern
                updated_lines.append(line.rstrip('; .') + f',')
                updated_lines.append(f'        <{json_entry["person"]}> ;')
                changes.append(f"Added sameAs: {json_entry['person']}")
                line_modified = True
            else:
                updated_lines.append(line)
        
        # Überprüfe und aktualisiere birthDate
        elif 'schema:birthDate' in line and json_entry.get('birthDate'):
            json_date = format_date_for_ttl(json_entry['birthDate'])
            current_date = block_data.get('birthDate')
            if current_date and current_date != json_date.replace('"^^xsd:date', ''):
                # Kommentiere alten Wert aus und füge neuen hinzu
                old_value = re.search(r'"([^"]+)"', line).group(1) if '"' in line else 'unknown'
                updated_lines.append(f"    # ORIGINAL: {line.strip()}")
                updated_lines.append(f'    schema:birthDate "{json_date}"')
                changes.append(f"Updated birthDate from {old_value} to {json_date}")
                line_modified = True
            else:
                updated_lines.append(line)
        
        # Überprüfe und aktualisiere birthPlace
        elif 'schema:birthPlace' in line and json_entry.get('birthPlace'):
            current_place = block_data.get('birthPlace')
            if current_place and current_place != json_entry['birthPlace']:
                updated_lines.append(f"    # ORIGINAL: {line.strip()}")
                updated_lines.append(f'    schema:birthPlace <{json_entry["birthPlace"]}>')
                changes.append(f"Updated birthPlace from {current_place} to {json_entry['birthPlace']}")
                line_modified = True
            else:
                updated_lines.append(line)
        
        # Überprüfe und aktualisiere deathDate
        elif 'schema:deathDate' in line and json_entry.get('deathDate'):
            json_date = format_date_for_ttl(json_entry['deathDate'])
            current_date = block_data.get('deathDate')
            if current_date and current_date != json_date.replace('"^^xsd:date', ''):
                old_value = re.search(r'"([^"]+)"', line).group(1) if '"' in line else 'unknown'
                updated_lines.append(f"    # ORIGINAL: {line.strip()}")
                updated_lines.append(f'    schema:deathDate "{json_date}"')
                changes.append(f"Updated deathDate from {old_value} to {json_date}")
                line_modified = True
            else:
                updated_lines.append(line)
        
        # Überprüfe und aktualisiere deathPlace
        elif 'schema:deathPlace' in line and json_entry.get('deathPlace'):
            current_place = block_data.get('deathPlace')
            if current_place and current_place != json_entry['deathPlace']:
                updated_lines.append(f"    # ORIGINAL: {line.strip()}")
                updated_lines.append(f'    schema:deathPlace <{json_entry["deathPlace"]}>')
                changes.append(f"Updated deathPlace from {current_place} to {json_entry['deathPlace']}")
                line_modified = True
            else:
                updated_lines.append(line)
        
        # Wenn die Zeile nicht geändert wurde, übernehme sie unverändert
        if not line_modified and 'schema:sameAs' not in line:
            updated_lines.append(line)
        
        i += 1
    
    # Phase 2: Komplett fehlende Properties hinzufügen
    updated_lines, missing_changes = add_missing_properties(block_data, json_entry, updated_lines)
    changes.extend(missing_changes)
    
    # Phase 3: TTL-Syntax korrigieren (Zeichensetzung)
    updated_lines = ensure_correct_punctuation(updated_lines)
    
    # Entferne doppelte Punkte am Ende
    if len(updated_lines) >= 2 and updated_lines[-1].strip() == '.' and updated_lines[-2].strip() == '.':
        updated_lines.pop(-1)
    
    return '\n'.join(updated_lines), changes

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
            
            # Zeige fehlende Properties an
            missing = []
            if not block_data['has_sameAs'] and json_entry.get('person'):
                missing.append("sameAs")
            if not block_data['has_birthDate'] and json_entry.get('birthDate'):
                missing.append("birthDate")
            if not block_data['has_birthPlace'] and json_entry.get('birthPlace'):
                missing.append("birthPlace")
            if not block_data['has_deathDate'] and json_entry.get('deathDate'):
                missing.append("deathDate")
            if not block_data['has_deathPlace'] and json_entry.get('deathPlace'):
                missing.append("deathPlace")
            
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
    print(f"Anzahl durchgeführter Änderungen: {len(total_changes)}")
    
    if total_changes:
        print("\nDetails der Änderungen:")
        change_types = {}
        for subject, change in total_changes:
            change_type = change.split(':')[0] if ':' in change else change
            change_types[change_type] = change_types.get(change_type, 0) + 1
            print(f"  {subject}: {change}")
        
        print("\nZusammenfassung nach Typ:")
        for change_type, count in change_types.items():
            print(f"  {change_type}: {count}")

if __name__ == "__main__":
    main()