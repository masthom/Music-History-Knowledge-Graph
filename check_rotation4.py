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
    rotation_groups = []
    used_patterns = set()
    
    for closed_pat, originals in closed_map.items():
        if closed_pat in used_patterns:
            continue
            
        # Finde alle Rotationen dieses geschlossenen Musters
        rotations = generate_rotations(closed_pat)
        current_group = set()
        
        # Sammle alle originalen Intervallpatterns, die zu diesen Rotationen gehören
        for rot in rotations:
            if rot in closed_map:
                current_group.update(closed_map[rot])
                used_patterns.add(rot)
        
        if len(current_group) > 1:
            rotation_groups.append(current_group)
    
    print(f"Gefundene Rotationsgruppen: {len(rotation_groups)}")
    
    # Schreibe die Ausgabedatei
    with open(output_ttl_path, 'w', encoding='utf-8') as f:
        # Schreibe isRotationOf-Beziehungen für alle Paare in jeder Gruppe
        for group in rotation_groups:
            group_list = list(group)
            # Erzeuge alle Paare innerhalb der Gruppe
            for i in range(len(group_list)):
                for j in range(i+1, len(group_list)):
                    a = group_list[i]
                    b = group_list[j]
                    f.write(f"mhg:ip_{a} mhg:isRotationOf mhg:ip_{b} .\n")
                    f.write(f"mhg:ip_{b} mhg:isRotationOf mhg:ip_{a} .\n")
        
        # Schreibe hasRotations-Beziehungen für die kleinste Pattern jeder Gruppe
        for group in rotation_groups:
            sorted_group = sorted(group, key=lambda x: [int(n) for n in x.split('_')])
            smallest = sorted_group[0]
            rotations_list = ", ".join([f"mhg:ip_{r}" for r in sorted_group[1:]])
            f.write(f"mhg:ip_{smallest} mhg:hasRotations {rotations_list} .\n")

if __name__ == "__main__":
    input_ttl = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"  # Ihre Test-Datei
    output_ttl = "rotation_results4.ttl"
    process_ttl_file(input_ttl, output_ttl)