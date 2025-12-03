# Twelve-Tone Row Form Generator
# Workflow:
# 1) Berechne P0, I0, R0, RI0 aus Eingabe
# 2) Wähle lexikographisch kleinstes dieser vier Muster -> neue P
# 3) Berechne neue I, R, RI aus dieser neuen P
# 4) Erzeuge RowForms (P, I, R, RI) konsistent zur neuen P
# 5) Liefere Mapping (ursprünglich -> neu)

def invert_intervals(intervals):
    """Invertiert Intervalle: i -> (12 - i) % 12"""
    return [(12 - x) % 12 for x in intervals]

def reverse_intervals(intervals):
    """Gibt die Intervalle rückwärts zurück"""
    return list(reversed(intervals))

def generate_rows_from_interval_pattern(interval_list):
    """
    Erzeugt 12 Reihen (Startnoten 0..11) aus einem Intervallmuster,
    indem sukzessiv Intervalle addiert werden.
    """
    rows = []
    for start in range(12):
        row = [start]
        current = start
        for iv in interval_list:
            current = (current + iv) % 12
            row.append(current)
        rows.append(row)
    return rows

def intervals_to_str(intervals):
    return '_'.join(str(x) for x in intervals)

def compute_and_normalize(interval_pattern_str):
    """
    1) Berechnet die vier Ausgangsformen P0, I0, R0, RI0 (als Listen)
    2) Wählt lexikographisch das kleinste dieser vier Muster als neue P
    3) Erzeugt daraus neue I, R, RI
    4) Generiert die RowForms zu dieser neuen Zuordnung
    5) Ermittelt das Mapping (ursprünglich -> neu)
    """
    # Eingabe parsen
    base_P0 = [int(x) for x in interval_pattern_str.split('_')]

    # Ausgangs-Intervallmuster berechnen
    P0 = base_P0
    I0 = invert_intervals(P0)
    R0 = reverse_intervals(P0)
    RI0 = reverse_intervals(I0)

    originals = {
        "P": P0,
        "I": I0,
        "R": R0,
        "RI": RI0
    }

    # Bestimme lexikographisch kleinstes Muster
    # sorted_items: list of tuples (label, pattern) sorted by pattern
    sorted_items = sorted(originals.items(), key=lambda it: it[1])
    # Kleinstes ist sorted_items[0]
    smallest_old_label, smallest_pattern = sorted_items[0]

    # Setze neue P auf das kleinste Muster
    new_P = list(smallest_pattern)  # Kopie

    # Berechne konsistent neue I, R, RI aus new_P
    new_I = invert_intervals(new_P)
    new_R = reverse_intervals(new_P)
    new_RI = reverse_intervals(new_I)

    normalized = {
        "P": new_P,
        "I": new_I,
        "R": new_R,
        "RI": new_RI
    }

    # Erzeuge RowForms zu den normalisierten Mustern
    # Prime: aus new_P (intervals as given)
    prime_forms = generate_rows_from_interval_pattern(new_P)
    # Inversion-Interval-Liste für Reihen ist -new_P modulo 12:
    inversion_interval_list = [(-x) % 12 for x in new_P]
    inversion_forms = generate_rows_from_interval_pattern(inversion_interval_list)
    retrograde_forms = [list(reversed(r)) for r in prime_forms]
    retrograde_inversion_forms = [list(reversed(r)) for r in inversion_forms]

    row_forms = {
        "P": prime_forms,
        "I": inversion_forms,
        "R": retrograde_forms,
        "RI": retrograde_inversion_forms
    }

    # Erzeuge Mapping (ursprünglich -> neu)
    # Für jedes ursprüngliches Label bestimme, welchem neuen Label sein Pattern entspricht.
    mapping_old_to_new = {}
    # normalized patterns -> allow quick compare
    norm_to_label = {tuple(v): k for k, v in normalized.items()}
    for old_label, old_pattern in originals.items():
        t = tuple(old_pattern)
        if t in norm_to_label:
            mapping_old_to_new[old_label] = norm_to_label[t]
        else:
            # Sollte nicht passieren, aber als Fallback:
            # Falls das ursprüngliche Muster nicht genau einem der neu berechneten Muster entspricht,
            # finde dasjenige mit gleicher Inhalte (sicherer Vergleich) oder setze None.
            found = None
            for k, v in normalized.items():
                if tuple(v) == t:
                    found = k
                    break
            mapping_old_to_new[old_label] = found

    # Zusätzlich in String-Form für Ausgabe
    normalized_str = {k: intervals_to_str(v) for k, v in normalized.items()}

    return {
        "originals": {k: intervals_to_str(v) for k, v in originals.items()},
        "normalized_intervals": normalized_str,
        "row_forms": row_forms,
        "mapping": mapping_old_to_new
    }

def format_row_name(row):
    return '_'.join(str(x) for x in row)

def generate_ttl_output_from_forms(forms):
    """
    Baut die TTL-ähnliche Ausgabe basierend auf den normalisierten Mustern und RowForms.
    """
    patterns = forms["normalized_intervals"]
    rows = forms["row_forms"]

    p_pattern = patterns["P"]
    i_pattern = patterns["I"]
    r_pattern = patterns["R"]
    ri_pattern = patterns["RI"]

    prime_forms = rows["P"]
    inversion_forms = rows["I"]
    retrograde_forms = rows["R"]
    retrograde_inversion_forms = rows["RI"]

    output = []
    output.append("# Normalisierte Intervallmuster")
    output.append(f"# P: {p_pattern}")
    output.append(f"# I: {i_pattern}")
    output.append(f"# R: {r_pattern}")
    output.append(f"# RI: {ri_pattern}")
    output.append(f"mhg:{p_pattern} a mhg:rowClass ;")
    output.append("    mhg:hasRowForm")

    # P-Forms
    output.append("        # P-Forms (0-11)")
    for i, row in enumerate(prime_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # I-Forms
    output.append("        \n        # I-Forms (0-11)")
    for i, row in enumerate(inversion_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # R-Forms
    output.append("        \n        # R-Forms (0-11)")
    for i, row in enumerate(retrograde_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # RI-Forms
    output.append("        \n        # RI-Forms (0-11)")
    for i, row in enumerate(retrograde_inversion_forms):
        suffix = "," if i < 11 else " ."
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # RowForm-Deklarationen
    output.append("\n# RowForm-Deklarationen")
    for row in prime_forms + inversion_forms + retrograde_forms + retrograde_inversion_forms:
        name = format_row_name(row)
        output.append(f"mhg:{name} a mhg:rowForm ; mhg:hasRowClass mhg:{p_pattern} .")

    return "\n".join(output)

def main():
    example = "1_3_1_6_11_5_4_2_9_2_6"
    print("Twelve-Tone Row Forms Generator (P-Normalisierung nach kleinstem Intervallmuster)")
    print("===========================================================================")
    user_input = input(f"Intervallmuster eingeben (Enter für Beispiel '{example}'): ").strip()
    if user_input:
        pattern = user_input
    else:
        pattern = example

    try:
        result = compute_and_normalize(pattern)

        print("\nUrsprüngliche Intervallmuster (aus P0):")
        for k, v in result["originals"].items():
            print(f"{k}: {v}")

        print("\nNormalisierte Intervallmuster (neu benannt, kleinste -> P):")
        for k, v in result["normalized_intervals"].items():
            print(f"{k}: {v}")

        print("\nMapping (ursprünglich -> neu):")
        for old, new in result["mapping"].items():
            print(f"{old} -> {new}")

        print("\nTTL-Ausgabe:\n")
        ttl = generate_ttl_output_from_forms(result)
        print(ttl)

    except Exception as e:
        print("Fehler:", e)
        print("Bitte ein korrektes Intervallmuster im Format 'a_b_c_...' eingeben (z.B. 5_1_3_2).")

if __name__ == "__main__":
    main()
