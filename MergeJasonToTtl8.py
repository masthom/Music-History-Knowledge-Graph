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
    
    # sameAs Links extrahieren - erfasst alle Links in der sameAs-Property
    sameas_pattern = r'schema:sameAs\s+([^;]+);'
    sameas_match = re.search(sameas_pattern, block, re.DOTALL)
    if sameas_match:
        sameas_content = sameas_match.group(1)
        # Finde alle URLs in dem Content
        url_pattern = r'<([^>]+)>'
        data['sameAs'] = re.findall(url_pattern, sameas_content)
        data['has_sameAs'] = len(data['sameAs']) > 0
    
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

def remove_duplicate_properties(lines):
    """Entfernt doppelte Property-Einträge aus den Zeilen"""
    seen_properties = set()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Identifiziere den Property-Typ
        prop_type = None
        if 'schema:birthDate' in stripped and not stripped.startswith('#'):
            prop_type = 'birthDate'
        elif 'schema:birthPlace' in stripped and not stripped.startswith('#'):
            prop_type = 'birthPlace' 
        elif 'schema:deathDate' in stripped and not stripped.startswith('#'):
            prop_type = 'deathDate'
        elif 'schema:deathPlace' in stripped and not stripped.startswith('#'):
            prop_type = 'deathPlace'
        elif 'schema:sameAs' in stripped and not stripped.startswith('#'):
            prop_type = 'sameAs'
        
        # Wenn Property bereits gesehen, überspringe diese Zeile
        if prop_type and prop_type in seen_properties:
            continue
            
        if prop_type:
            seen_properties.add(prop_type)
            
        cleaned_lines.append(line)
    
    return cleaned_lines

def remove_placeholder_comments(lines):
    """Entfernt Platzhalter-Kommentare wie # schema:birthDate "YYYY-MM-DD" ;"""
    cleaned_lines = []
    placeholder_patterns = [
        r'#\s*schema:birthDate\s+"YYYY-MM-DD"',
        r'#\s*schema:deathDate\s+"YYYY-MM-DD"', 
        r'#\s*schema:birthPlace\s+"\.\.\."',
        r'#\s*schema:sameAs\s+<\.\.\.>',
        r'#\s*schema:birthDate\s+"..."',
        r'#\s*schema:deathDate\s+"..."'
    ]
    
    for line in lines:
        if any(re.search(pattern, line) for pattern in placeholder_patterns):
            continue
        cleaned_lines.append(line)
    
    return cleaned_lines

def ensure_correct_punctuation(lines):
    """Stellt korrekte TTL-Zeichensetzung sicher"""
    if not lines:
        return lines
        
    # Finde die letzte nicht-Kommentar, nicht-leere Zeile
    last_content_idx = -1
    for i in range(len(lines)-1, -1, -1):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith('#') and stripped != '.':
            last_content_idx = i
            break
    
    if last_content_idx == -1:
        return lines
    
    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Leere Zeilen und Kommentare unverändert übernehmen
        if not stripped or stripped.startswith('#'):
            result.append(line)
            continue
            
        # Wenn es die letzte Inhaltszeile ist, muss sie mit . enden
        if i == last_content_idx:
            # Entferne vorhandene Semikolons oder Punkte am Ende
            clean_line = line.rstrip().rstrip(';').rstrip('.')
            result.append(clean_line + ' .')
        else:
            # Normale Property-Zeilen müssen mit ; enden (wenn nicht schon vorhanden)
            if not stripped.endswith(';') and not stripped.endswith(',') and not stripped.endswith('.'):
                result.append(line.rstrip() + ' ;')
            else:
                result.append(line)
    
    return result

def update_ttl_block(block_data, json_entry):
    """Aktualisiert einen TTL-Block basierend auf JSON-Daten"""
    changes = []
    lines = block_data['raw_lines'].copy()
    
    # Phase 1: Entferne Platzhalter-Kommentare
    lines = remove_placeholder_comments(lines)
    
    # Phase 2: Entferne doppelte Properties
    lines = remove_duplicate_properties(lines)
    
    # Phase 3: Erstelle neue Properties
    new_properties = []
    
    # sameAs - kombinere vorhandene mit neuem Wikidata-Link
    if json_entry.get('person'):
        all_sameas = block_data['sameAs'].copy()
        if json_entry['person'] not in all_sameas:
            all_sameas.append(json_entry['person'])
            changes.append(f"Added sameAs: {json_entry['person']}")
        
        if all_sameas:
            # Erstelle sameAs als mehrzeilige Liste
            sameas_lines = ['    schema:sameAs']
            for i, link in enumerate(all_sameas):
                if i == 0:
                    sameas_lines.append(f'        <{link}>')
                else:
                    sameas_lines.append(f'        , <{link}>')
            sameas_lines[-1] = sameas_lines[-1] + ' ;'
            new_properties.append(('\n'.join(sameas_lines), 'sameAs'))
    
    # birthDate
    if json_entry.get('birthDate'):
        formatted_date = format_date_for_ttl(json_entry['birthDate'])
        if block_data.get('birthDate') and block_data['birthDate'] != formatted_date.replace('"^^xsd:date', ''):
            new_properties.append((f'    # ORIGINAL: schema:birthDate "{block_data["birthDate"]}"^^xsd:date ;\n    schema:birthDate "{formatted_date}" ;', 'birthDate'))
            changes.append(f"Updated birthDate from {block_data['birthDate']} to {formatted_date}")
        elif not block_data.get('birthDate'):
            new_properties.append((f'    schema:birthDate "{formatted_date}" ;', 'birthDate'))
            changes.append(f"Added birthDate: {formatted_date}")
    
    # birthPlace
    if json_entry.get('birthPlace'):
        if block_data.get('birthPlace') and block_data['birthPlace'] != json_entry['birthPlace']:
            new_properties.append((f'    # ORIGINAL: schema:birthPlace <{block_data["birthPlace"]}> ;\n    schema:birthPlace <{json_entry["birthPlace"]}> ;', 'birthPlace'))
            changes.append(f"Updated birthPlace from {block_data['birthPlace']} to {json_entry['birthPlace']}")
        elif not block_data.get('birthPlace'):
            new_properties.append((f'    schema:birthPlace <{json_entry["birthPlace"]}> ;', 'birthPlace'))
            changes.append(f"Added birthPlace: {json_entry['birthPlace']}")
    
    # deathDate
    if json_entry.get('deathDate'):
        formatted_date = format_date_for_ttl(json_entry['deathDate'])
        if block_data.get('deathDate') and block_data['deathDate'] != formatted_date.replace('"^^xsd:date', ''):
            new_properties.append((f'    # ORIGINAL: schema:deathDate "{block_data["deathDate"]}"^^xsd:date ;\n    schema:deathDate "{formatted_date}" ;', 'deathDate'))
            changes.append(f"Updated deathDate from {block_data['deathDate']} to {formatted_date}")
        elif not block_data.get('deathDate'):
            new_properties.append((f'    schema:deathDate "{formatted_date}" ;', 'deathDate'))
            changes.append(f"Added deathDate: {formatted_date}")
    
    # deathPlace
    if json_entry.get('deathPlace'):
        if block_data.get('deathPlace') and block_data['deathPlace'] != json_entry['deathPlace']:
            new_properties.append((f'    # ORIGINAL: schema:deathPlace <{block_data["deathPlace"]}> ;\n    schema:deathPlace <{json_entry["deathPlace"]}> ;', 'deathPlace'))
            changes.append(f"Updated deathPlace from {block_data['deathPlace']} to {json_entry['deathPlace']}")
        elif not block_data.get('deathPlace'):
            new_properties.append((f'    schema:deathPlace <{json_entry["deathPlace"]}> ;', 'deathPlace'))
            changes.append(f"Added deathPlace: {json_entry['deathPlace']}")
    
    # Phase 4: Entferne vorhandene Properties, die wir ersetzen wollen
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
                # Wenn es sich um sameAs handelt, müssen wir die gesamte Property (mehrere Zeilen) entfernen
                if prop == 'schema:sameAs':
                    # Überspringe diese Zeile und alle folgenden, die mit Komma beginnen
                    cleaned_lines.append(line)  # Behalte die Zeile vorerst
                    i += 1
                    while i < len(lines) and (lines[i].strip().startswith(',') or lines[i].strip().startswith('<')):
                        i += 1
                    remove_line = True
                    break
                else:
                    remove_line = True
                    break
        
        if not remove_line:
            cleaned_lines.append(line)
        i += 1
    
    lines = cleaned_lines
    
    # Phase 5: Füge neue Properties an der richtigen Position ein
    # Finde Einfügeposition nach schema:name
    insert_pos = -1
    for i, line in enumerate(lines):
        if 'schema:name' in line and not line.strip().startswith('#'):
            # Gehe zur nächsten Zeile nach schema:name
            insert_pos = i + 1
            # Überspringe eventuelle Kommentare
            while insert_pos < len(lines) and (not lines[insert_pos].strip() or lines[insert_pos].strip().startswith('#')):
                insert_pos += 1
            break
    
    if insert_pos == -1:
        # Fallback: Füge vor dem schließenden Punkt ein
        for i, line in enumerate(lines):
            if line.strip() == '.':
                insert_pos = i
                break
        if insert_pos == -1:
            insert_pos = len(lines)
    
    # Füge Properties in umgekehrter Reihenfolge ein
    for prop_content, prop_type in reversed(new_properties):
        lines.insert(insert_pos, prop_content)
    
    # Phase 6: Korrigiere Zeichensetzung
    lines = ensure_correct_punctuation(lines)
    
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