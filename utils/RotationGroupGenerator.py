# last updated: 2025-12-04
import re
import sys

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

def validate_pattern(pattern):
    """Validiert, ob ein Pattern gültig ist"""
    if not pattern:
        return False, "Pattern ist leer"
    
    # Entferne "ip_" Präfix falls vorhanden
    if pattern.startswith('ip_'):
        pattern = pattern[3:]
    
    # Prüfe Format
    parts = pattern.split('_')
    if not all(parts):
        return False, "Pattern enthält leere Teile"
    
    # Prüfe ob alle Teile Zahlen sind
    for part in parts:
        try:
            int(part)
        except ValueError:
            return False, f"'{part}' ist keine gültige Zahl"
    
    return True, pattern

def process_single_pattern(input_pattern, output_ttl_path=None):
    """
    Verarbeitet ein einzelnes Intervallpattern und generiert seine Rotationsgruppe
    
    Args:
        input_pattern: Das Intervallpattern (z.B. "1_2_3" oder "ip_1_2_3")
        output_ttl_path: Optionaler Pfad für die Ausgabedatei
    """
    # Validiere das Pattern
    is_valid, result = validate_pattern(input_pattern)
    if not is_valid:
        print(f"Fehler: {result}")
        return None
    
    pattern = result
    print(f"Verarbeite Pattern: {pattern}")
    
    try:
        # Berechne die geschlossene Form
        closed = calculate_closure_interval(pattern)
        n = len(pattern.split('_'))
        
        print(f"Geschlossene Form: {closed}")
        print(f"Länge: {n}")
        
        # Generiere Rotationen der geschlossenen Form
        rotations_closed = generate_rotations(closed)
        canonical_closed = find_canonical_group_name(rotations_closed)
        
        print(f"Kanonische geschlossene Form: {canonical_closed}")
        
        # Generiere alle Rotationen der kanonischen geschlossenen Form
        all_rotations_closed = generate_rotations(canonical_closed)
        
        # Kürze auf ursprüngliche Länge für die Gruppenelemente
        group_members = []
        for closed_rotation in all_rotations_closed:
            parts = closed_rotation.split('_')
            shortened = '_'.join(parts[:n])
            group_members.append(shortened)
        
        # Der kanonische Name ist das erste Element
        canonical_name = group_members[0]
        
        print(f"\nRotationsgruppen-Mitglieder ({len(group_members)}):")
        for i, member in enumerate(group_members):
            print(f"  {i}: {member}")
        
        # Finde Index des Eingabe-Patterns
        pattern_index = group_members.index(pattern)
        print(f"\nEingabe-Pattern '{pattern}' hat Index {pattern_index} in der Gruppe")
        
        # Wenn Ausgabedatei angegeben, schreibe TTL
        if output_ttl_path:
            write_ttl_output(pattern, group_members, canonical_name, pattern_index, output_ttl_path)
            print(f"\nAusgabe wurde geschrieben nach: {output_ttl_path}")
        
        return {
            'input_pattern': pattern,
            'closed_form': closed,
            'canonical_closed': canonical_closed,
            'group_members': group_members,
            'canonical_name': canonical_name,
            'pattern_index': pattern_index
        }
    
    except Exception as e:
        print(f"Fehler bei der Verarbeitung: {e}")
        return None

def write_ttl_output(input_pattern, group_members, canonical_name, pattern_index, output_path):
    """Schreibt die Rotationsgruppe als TTL-Datei"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Schreibe die Rotationsgruppe
        group_uri = f"mhg:rotationGroup_{canonical_name}"
        f.write(f"{group_uri} a mhg:rotationGroup ;\n")
        f.write("    mhg:hasRotationGroupElement ")
        
        # Füge alle Gruppenmitglieder hinzu
        elements = []
        for i, rotation in enumerate(group_members):
            element = f"mhg:ip_{rotation}"
            suffix = "," if i < len(group_members) - 1 else "."
            
            if rotation == input_pattern:
                line = f"{element} {suffix}"
            else:
                line = f"{element} {suffix}  ##not yet detected"
            
            elements.append(line)
        
        # Füge die Liste mit korrekter Einrückung ein
        f.write("\n                 ".join(elements) + "\n\n")
        
        # Schreibe das Eingabe-Pattern
        f.write(f"mhg:ip_{input_pattern} a mhg:intervalPattern ;\n")
        f.write(f"    mhg:hasRotationGroup {group_uri} ;\n")
        f.write(f"    mhg:rotationIndex {pattern_index} .\n")

def interactive_mode():
    """Interaktiver Modus für Benutzereingabe"""
    print("=== Intervallpattern Rotationsgruppen Generator ===")
    print("Geben Sie ein Intervallpattern ein (z.B. '1_2_3' oder 'ip_1_2_3')")
    print("oder 'exit' zum Beenden.\n")
    
    while True:
        user_input = input("Pattern: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Programm beendet.")
            break
        
        if not user_input:
            continue
        
        result = process_single_pattern(user_input)
        
        if result:
            print("\n" + "="*50 + "\n")

def print_usage():
    """Zeigt die Verwendungsmöglichkeiten an"""
    print("Verwendung:")
    print("  python skript.py <pattern> [output_file]")
    print("\nBeispiele:")
    print("  python skript.py 1_2_3")
    print("  python skript.py ip_1_2_3")
    print("  python skript.py 4_5 rotations.ttl")
    print("  python skript.py (interaktiver Modus)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Kommandozeilenmodus
        input_pattern = sys.argv[1]
        
        # Hilfe anzeigen
        if input_pattern in ['-h', '--help', '/?']:
            print_usage()
            sys.exit(0)
        
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            # Generiere Standard-Ausgabedateinamen
            pattern_name = input_pattern.replace('ip_', '').replace('_', '-')
            output_file = f"rotation_group_{pattern_name}.ttl"
        
        process_single_pattern(input_pattern, output_file)
    else:
        # Interaktiver Modus
        interactive_mode()