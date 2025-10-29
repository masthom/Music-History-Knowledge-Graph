#Python 3.10.5 (tags/v3.10.5:f377153, Jun  6 2022, 16:14:13) [MSC v.1929 64 bit (AMD64)] on win32
#Type "help", "copyright", "credits" or "license()" for more information.
def generate_row_forms(interval_pattern):
    """
    Generiert alle 48 RowForms basierend auf einem Intervallmuster
    """
    # Konvertiere Intervallmuster in Liste von Integers
    intervals = [int(x) for x in interval_pattern.split('_')]
    
    # 1. PRIME-FORMS (P-Forms)
    prime_forms = []
    for start_note in range(12):
        row = [start_note]
        current_note = start_note
        for interval in intervals:
            current_note = (current_note + interval) % 12
            row.append(current_note)
        prime_forms.append(row)
    
    # 2. INVERSION-FORMS (I-Forms)
    inversion_forms = []
    for start_note in range(12):
        row = [start_note]
        current_note = start_note
        for interval in intervals:
            current_note = (current_note - interval) % 12
            row.append(current_note)
        inversion_forms.append(row)
    
    # 3. RETROGRADE-FORMS (R-Forms) - Umgekehrte Prime-Forms
    retrograde_forms = []
    for p_form in prime_forms:
        retrograde_forms.append(list(reversed(p_form)))
    
    # 4. RETROGRADE-INVERSION-FORMS (RI-Forms) - Umgekehrte Inversion-Forms
    retrograde_inversion_forms = []
    for i_form in inversion_forms:
        retrograde_inversion_forms.append(list(reversed(i_form)))
    
    return prime_forms, inversion_forms, retrograde_forms, retrograde_inversion_forms

def format_row_name(row):
    """Formatiert eine Row als String mit Unterstrichen"""
    return '_'.join(str(note) for note in row)

def generate_ttl_output(interval_pattern, prime_forms, inversion_forms, retrograde_forms, retrograde_inversion_forms):
    """Generiert die TTL-Ausgabe"""
    
    # Berechne die anderen Intervallmuster für die Kommentare
    intervals = [int(x) for x in interval_pattern.split('_')]
    
    # P-Intervallmuster (Eingabe)
    p_pattern = interval_pattern
    
    # I-Intervallmuster (negative Intervalle)
    i_pattern = '_'.join(str((-int(x)) % 12) for x in intervals)
    
    # R-Intervallmuster (umgekehrt)
    r_pattern = '_'.join(str(x) for x in reversed(intervals))
    
    # RI-Intervallmuster (umgekehrt und negiert)
    ri_pattern = '_'.join(str((-int(x)) % 12) for x in reversed(intervals))
    
    output = []
    output.append(f"# P: {p_pattern}")
    output.append(f"# I: {i_pattern}")
    output.append(f"# R: {r_pattern}")
    output.append(f"# RI: {ri_pattern}")
    output.append(f"mhg:{p_pattern} a mhg:RowClass ;")
    output.append("    mhg:hasRowForm")
    
    # P-Forms
    output.append("        # P-Forms (0-11)")
    for i, row in enumerate(prime_forms):
        prefix = "        " if i == 0 else "        "
        suffix = "," if i < 11 else " ,"
        output.append(f"{prefix}mhg:{format_row_name(row)}{suffix}")
    
    # I-Forms
    output.append("        \n        # I-Forms (0-11)")
    for i, row in enumerate(inversion_forms):
        prefix = "        " if i == 0 else "        "
        suffix = "," if i < 11 else " ,"
        output.append(f"{prefix}mhg:{format_row_name(row)}{suffix}")
    
    # R-Forms
    output.append("        \n        # R-Forms (0-11)")
    for i, row in enumerate(retrograde_forms):
        prefix = "        " if i == 0 else "        "
        suffix = "," if i < 11 else " ,"
        output.append(f"{prefix}mhg:{format_row_name(row)}{suffix}")
    
    # RI-Forms
    output.append("        \n        # RI-Forms (0-11)")
    for i, row in enumerate(retrograde_inversion_forms):
        prefix = "        " if i == 0 else "        "
        suffix = "," if i < 11 else " ."
        output.append(f"{prefix}mhg:{format_row_name(row)}{suffix}")
    
    # RowForm-Deklarationen
    output.append("\n# RowForm-Deklarationen")
    
    for row in prime_forms + inversion_forms + retrograde_forms + retrograde_inversion_forms:
        row_name = format_row_name(row)
        output.append(f"mhg:{row_name} a mhg:rowForm ; mhg:hasRowClass mhg:{p_pattern} .")
    
    return '\n'.join(output)

def main():
    # Beispiel-Intervallmuster
    interval_pattern = "1_3_1_6_11_5_4_2_9_2_6"
    
    print("Twelve-Tone Row Forms Generator")
    print("===============================")
    
    # Benutzer kann eigenes Intervallmuster eingeben
    user_input = input(f"Intervallmuster eingeben (Enter für Beispiel '{interval_pattern}'): ").strip()
    if user_input:
        interval_pattern = user_input
    
    try:
        # Generiere alle RowForms
        prime_forms, inversion_forms, retrograde_forms, retrograde_inversion_forms = generate_row_forms(interval_pattern)
        
        # Generiere TTL-Ausgabe
        ttl_output = generate_ttl_output(interval_pattern, prime_forms, inversion_forms, retrograde_forms, retrograde_inversion_forms)
        
        print("\n" + "="*50)
        print("TTL-AUSGABE:")
        print("="*50)
        print(ttl_output)
        
        # Zusätzliche Informationen
        print("\n" + "="*50)
        print("ZUSAMMENFASSUNG:")
        print("="*50)
        print(f"RowClass: mhg:{interval_pattern}")
        print(f"Anzahl P-Forms: {len(prime_forms)}")
        print(f"Anzahl I-Forms: {len(inversion_forms)}")
        print(f"Anzahl R-Forms: {len(retrograde_forms)}")
        print(f"Anzahl RI-Forms: {len(retrograde_inversion_forms)}")
        print(f"Gesamtanzahl RowForms: {len(prime_forms) + len(inversion_forms) + len(retrograde_forms) + len(retrograde_inversion_forms)}")
        
        # Beispiel der ersten RowForms jeder Kategorie
        print(f"\nBeispiel P0: {format_row_name(prime_forms[0])}")
        print(f"Beispiel I0: {format_row_name(inversion_forms[0])}")
        print(f"Beispiel R0: {format_row_name(retrograde_forms[0])}")
        print(f"Beispiel RI0: {format_row_name(retrograde_inversion_forms[0])}")
        
    except Exception as e:
        print(f"Fehler: {e}")
        print("Stellen Sie sicher, dass das Intervallmuster im Format '1_2_3_4_5_6_7_8_9_10_11' eingegeben wurde.")

if __name__ == "__main__":
    main()