import re

def calculate_closure_interval(interval_pattern):
    """Berechnet die geschlossene Form eines Intervallmusters"""
    intervals = list(map(int, interval_pattern.split('_')))
    current_pc = 0
    for interval in intervals:
        current_pc = (current_pc + interval) % 12
    closure_interval = (0 - current_pc) % 12
    intervals.append(closure_interval)
    return '_'.join(map(str, intervals))

def generate_rotations(pattern_str):
    """Generiert alle Rotationen eines Musters"""
    parts = pattern_str.split('_')
    n = len(parts)
    rotations = []
    for i in range(n):
        rotated = parts[i:] + parts[:i]
        rotations.append('_'.join(rotated))
    return rotations

def find_canonical_group_name(patterns):
    """Findet den numerisch kleinsten String in einer Liste von Mustern"""
    return min(patterns, key=lambda x: [int(n) for n in x.split('_')])

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
    
    # Gruppiere nach kanonischer geschlossener Form
    closed_groups = {}
    for pattern in original_patterns:
        n = len(pattern.split('_'))
        closed = calculate_closure_interval(pattern)
        rotations = generate_rotations(closed)
        canonical_closed = find_canonical_group_name(rotations)
        
        if canonical_closed not in closed_groups:
            closed_groups[canonical_closed] = {
                'patterns': set(),
                'n': n
            }
        closed_groups[canonical_closed]['patterns'].add(pattern)
    
    print(f"Gefundene geschlossene Gruppen: {len(closed_groups)}")
    
    # Erstelle die Rotationsgruppen
    rotation_groups = {}
    for canonical_closed, group_data in closed_groups.items():
        n = group_data['n']
        patterns = group_data['patterns']
        
        # Generiere alle Rotationen der kanonischen geschlossenen Form
        all_rotations_closed = generate_rotations(canonical_closed)
        
        # Generiere die gekürzten Muster (ohne das letzte Intervall)
        group_members = []
        for closed_rotation in all_rotations_closed:
            parts = closed_rotation.split('_')
            shortened = '_'.join(parts[:n])  # Kürze auf ursprüngliche Länge
            group_members.append(shortened)
        
        # Der kanonische Name ist das erste Element (entspricht der kanonischen geschlossenen Form)
        canonical_name = group_members[0]
        
        rotation_groups[canonical_name] = {
            'all_rotations': group_members,
            'found_patterns': patterns
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
            for i, rotation in enumerate(all_rotations):

                element = f"mhg:ip_{rotation}"
                suffix = "," if i < len(all_rotations) - 1 else "."
    
                if rotation in found_patterns:
                    # Kein Kommentar
                    line = f"{element} {suffix}"
                else:
                    # Kommentar nach dem Suffix
                    line = f"{element} {suffix}  ##not yet detected"

                elements.append(line)

            
            # Füge die Liste mit korrekter Einrückung ein
            f.write("\n                 ".join(elements) + "\n\n")
            
            # Schreibe für jedes vorhandene Pattern die Triples mit korrektem Index
            for pattern in found_patterns:
                index = all_rotations.index(pattern)
                f.write(f"mhg:ip_{pattern} a mhg:intervalPattern ;\n")
                f.write(f"    mhg:hasRotationGroup {group_uri} ;\n")
                f.write(f"    mhg:rotationIndex {index} .\n\n")

if __name__ == "__main__":
    input_ttl = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"  # Ihre Test-Datei
    output_ttl = "rotation_results9.ttl"
    process_ttl_file(input_ttl, output_ttl)