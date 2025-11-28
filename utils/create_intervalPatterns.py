import re

def compute_transformations(pattern):
    """Berechnet P, I, R und RI Transformationen für ein Intervallmuster"""
    intervals = pattern.split('_')
    
    # P-Form (Original)
    P = pattern
    
    # I-Form (12 - jedes Intervall)
    I_intervals = [str((12 - int(x)) % 12) for x in intervals]
    I = '_'.join(I_intervals)
    
    # R-Form (Umkehrung der Reihenfolge)
    R_intervals = intervals[::-1]
    R = '_'.join(R_intervals)
    
    # RI-Form (Umkehrung von I)
    RI_intervals = I_intervals[::-1]
    RI = '_'.join(RI_intervals)
    
    return P, I, R, RI

def process_ttl_file(input_ttl_path, output_ttl_path):
    # Regex zum Extrahieren der rowClass-Deklarationen
    pattern_extract = re.compile(r'(mhg:([0-9_]+)\s+a\s+mhg:rowClass\s*;[^.]*\.)')
    
    # Lese die Eingabedatei
    with open(input_ttl_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Finde alle rowClass-Blöcke
    matches = pattern_extract.findall(content)
    print(f"Gefundene rowClass-Blöcke: {len(matches)}")
    
    # Funktion zum Ersetzen der rowClass-Blöcke
    def replace_rowclass_block(match):
        full_block = match.group(1)
        pattern = match.group(2)
        
        # Berechne die Transformationen
        P, I, R, RI = compute_transformations(pattern)
        
        # Erstelle die neuen hasIntervalPattern-Triples
        new_has_interval_pattern = f"""
    mhg:hasIntervalPattern mhg:ip_{P} , ##P
    mhg:ip_{I} , ##I
    mhg:ip_{R} , ##R
    mhg:ip_{RI} ; ##RI"""
        
        # Füge die neuen Triples zum Block hinzu (vor dem abschließenden Punkt)
        # Wir suchen nach dem ersten Vorkommen von "a mhg:rowClass ;" und fügen danach ein
        block_with_new_triples = full_block.replace(
            ' a mhg:rowClass ;', 
            ' a mhg:rowClass ;' + new_has_interval_pattern, 
            1
        )
        
        # Erstelle die intervalPattern-Ressourcen
        interval_patterns = f"""
mhg:ip_{P} a mhg:intervalPattern ; 
mhg:hasRowClass mhg:{pattern} .
mhg:ip_{I} a mhg:intervalPattern ; 
mhg:hasRowClass mhg:{pattern} .
mhg:ip_{R} a mhg:intervalPattern ; 
mhg:hasRowClass mhg:{pattern} .
mhg:ip_{RI} a mhg:intervalPattern ; 
mhg:hasRowClass mhg:{pattern} ."""
        
        # Kombiniere den erweiterten Block mit den intervalPattern-Ressourcen
        return block_with_new_triples + interval_patterns
    
    # Ersetze alle rowClass-Blöcke
    new_content = pattern_extract.sub(replace_rowclass_block, content)
    
    # Schreibe die Ausgabedatei
    with open(output_ttl_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Transformierte TTL-Datei wurde erstellt: {output_ttl_path}")

if __name__ == "__main__":
    input_ttl = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"  # Ihre Test-Datei
    output_ttl = "transformations5.ttl"
    process_ttl_file(input_ttl, output_ttl)