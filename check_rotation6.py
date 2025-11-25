import re

def calculate_closure_interval(interval_pattern):
    intervals = list(map(int, interval_pattern.split('_')))
    current_pc = 0
    for interval in intervals:
        current_pc = (current_pc + interval) % 12
    closure_interval = (0 - current_pc) % 12
    intervals.append(closure_interval)
    return '_'.join(map(str, intervals))

def generate_rotations(pattern_str):
    parts = pattern_str.split('_')
    n = len(parts)
    rotations = []
    for i in range(n):
        rotated = parts[i:] + parts[:i]
        rotations.append('_'.join(rotated))
    return rotations

def get_all_rotations_for_group(closed_pattern):
    """Generiert alle 11-Interval-Rotationen aus einem geschlossenen 12-Interval-Muster"""
    rotations_12 = generate_rotations(closed_pattern)
    rotations_11 = []
    for rotation in rotations_12:
        parts = rotation.split('_')
        rotations_11.append('_'.join(parts[:11]))
    return rotations_11

def find_canonical_group_name(rotations_11):
    """Findet den numerisch kleinsten String in der Rotationsliste"""
    return min(rotations_11, key=lambda x: [int(n) for n in x.split('_')])

def process_ttl_file(input_ttl_path, output_ttl_path):
    # Regex zum Extrahieren der Intervallpattern-Muster
    pattern_extract = re.compile(r'mhg:ip_([0-9_]+)\s+a\s+mhg:intervalPattern\s*[;.]')
    original_patterns = set()
    
    # Lese die Eingabedatei und sammle alle Intervallpattern-Muster
    with open(input_ttl_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = pattern_extract.findall(content)
        for match in matches:
            original_patterns.add(match)
    
    print(f"Gefundene Intervallpattern-Muster: {len(original_patterns)}")
    
    # Berechne geschlossene Muster für jedes Intervallpattern
    closed_map = {}
    for pattern in original_patterns:
        closed_pattern = calculate_closure_interval(pattern)
        if closed_pattern not in closed_map:
            closed_map[closed_pattern] = set()
        closed_map[closed_pattern].add(pattern)
    
    print(f"Geschlossene Muster: {len(closed_map)}")
    
    # Finde Rotationsgruppen
    rotation_groups = {}
    used_patterns = set()
    
    for closed_pat, originals in closed_map.items():
        if closed_pat in used_patterns:
            continue
            
        # Generiere alle möglichen Rotationen für diese Gruppe
        all_rotations_11 = get_all_rotations_for_group(closed_pat)
        
        # Finde den kanonischen Gruppennamen (numerisch kleinste Rotation)
        canonical_name = find_canonical_group_name(all_rotations_11)
        
        # Sammle alle originalen Patterns, die zu dieser Gruppe gehören
        current_group = set()
        for rot in all_rotations_11:
            if rot in closed_map:
                current_group.update(closed_map[rot])
                used_patterns.add(rot)
        
        if len(current_group) > 1:
            rotation_groups[canonical_name] = {
                'closed_pattern': closed_pat,
                'all_rotations': all_rotations_11,
                'found_patterns': current_group
            }
    
    print(f"Gefundene Rotationsgruppen: {len(rotation_groups)}")
    
    # Schreibe die Ausgabedatei
    with open(output_ttl_path, 'w', encoding='utf-8') as f:
        # Schreibe die Rotationsgruppen und ihre Elemente
        for canonical_name, group_data in rotation_groups.items():
            all_rotations = group_data['all_rotations']
            found_patterns = group_data['found_patterns']
            
            # Erstelle die Rotationsgruppe mit kanonischem Namen
            group_uri = f"mhg:rotationGroup_{canonical_name}"
            f.write(f"{group_uri} a mhg:rotationGroup ;\n")
            f.write("    mhg:hasRotationGroupElement ")
            
            # Füge alle Gruppenmitglieder hinzu (vorhandene und fehlende)
            elements = []
            for rotation in all_rotations:
                if rotation in found_patterns:
                    elements.append(f"mhg:ip_{rotation}")
                else:
                    # Berechne das fehlende Abschlussintervall für den Kommentar
                    intervals = list(map(int, rotation.split('_')))
                    current_pc = 0
                    for interval in intervals:
                        current_pc = (current_pc + interval) % 12
                    closure_interval = (0 - current_pc) % 12
                    elements.append(f"# mhg:ip_{rotation}_{closure_interval}   ##not yet detected")
            
            # Füge die Liste als kommagetrennte Liste ein
            f.write(",\n                 ".join(elements) + " .\n\n")
            
            # Schreibe für jedes vorhandene Pattern die Triples mit korrektem Index
            for pattern in found_patterns:
                index = all_rotations.index(pattern)
                f.write(f"mhg:ip_{pattern} a mhg:intervalPattern ;\n")
                f.write(f"    mhg:hasRotationGroup {group_uri} ;\n")
                f.write(f"    mhg:rotationIndex {index} .\n\n")

if __name__ == "__main__":
    input_ttl = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"  # Ihre Test-Datei
    output_ttl = "rotation_results6.ttl"
    process_ttl_file(input_ttl, output_ttl)