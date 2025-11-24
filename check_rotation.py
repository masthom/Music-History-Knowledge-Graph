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
    # Korrigierte Regex - akzeptiert sowohl Punkte als auch Semikolons
    pattern_extract = re.compile(r'mhg:([0-9_]+)\s+a\s+mhg:rowClass\s*[;.]')
    original_patterns = set()
    
    # Lese die Eingabedatei und sammle alle Intervallmuster
    with open(input_ttl_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = pattern_extract.findall(content)
        for match in matches:
            original_patterns.add(match)
    
    print(f"Gefundene rowClass-Muster: {len(original_patterns)}")
    
    # Berechne geschlossene Muster für jedes Originalmuster
    closed_map = {}
    for pattern in original_patterns:
        closed_pattern = calculate_closure_interval(pattern)
        if closed_pattern not in closed_map:
            closed_map[closed_pattern] = set()
        closed_map[closed_pattern].add(pattern)
    
    print(f"Geschlossene Muster: {len(closed_map)}")
    
    # Finde Rotationsbeziehungen
    relations = set()
    for closed_pat, originals in closed_map.items():
        rotations = generate_rotations(closed_pat)
        
        for rot in rotations:
            if rot in closed_map:
                for original_a in originals:
                    for original_b in closed_map[rot]:
                        if original_a != original_b:
                            relations.add((original_a, original_b))
    
    print(f"Gefundene Rotationen: {len(relations)}")
    
    # Schreibe die Ausgabedatei mit korrekter TTL-Syntax
    with open(output_ttl_path, 'w', encoding='utf-8') as f:
        for a, b in relations:
            f.write(f"mhg:{a} mhg:isRotationOf mhg:{b} .\n")

if __name__ == "__main__":
    input_ttl = "MusicHistoryGraph_TwelveToneMusic_CompleteAdjust.ttl"  # Ihre Test-Datei
    output_ttl = "rotation_results.ttl"
    process_ttl_file(input_ttl, output_ttl)