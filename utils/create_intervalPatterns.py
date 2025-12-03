# Twelve-Tone Row Form Generator (integrierte Version)

def generate_all_forms(interval_pattern):
    """
    Berechnet P, I, R, RI Intervallmuster sowie alle zugehörigen
    RowForms (Prime, Inversion, Retrograde, Retrograde-Inversion).
    """
    # --- 1. Intervall-Transformationen ---
    intervals = [int(x) for x in interval_pattern.split('_')]

    # P = Original
    P = intervals

    # I = 12 - Intervall (Invertiert)
    I = [(12 - x) % 12 for x in intervals]

    # R = rückwärts (Retrograd von P)
    R = list(reversed(P))

    # RI = rückwärts von I
    RI = list(reversed(I))

    # --- 2. RowForms erzeugen ---
    def generate_rows(interval_list):
        """Erzeugt 12 Reihenformen eines Intervallmusters."""
        rows = []
        for start_note in range(12):
            row = [start_note]
            current = start_note
            for iv in interval_list:
                current = (current + iv) % 12
                row.append(current)
            rows.append(row)
        return rows

    prime_forms = generate_rows(P)
    inversion_forms = generate_rows([-x % 12 for x in P])  # klassische I-Reihe
    retrograde_forms = [list(reversed(row)) for row in prime_forms]
    retrograde_inversion_forms = [list(reversed(row)) for row in inversion_forms]

    return {
        "interval_patterns": {
            "P": '_'.join(str(x) for x in P),
            "I": '_'.join(str(x) for x in I),
            "R": '_'.join(str(x) for x in R),
            "RI": '_'.join(str(x) for x in RI),
        },
        "row_forms": {
            "P": prime_forms,
            "I": inversion_forms,
            "R": retrograde_forms,
            "RI": retrograde_inversion_forms,
        }
    }


def format_row_name(row):
    """Formatiert eine Row als String mit Unterstrichen"""
    return '_'.join(str(note) for note in row)


def generate_ttl_output(interval_pattern, forms):
    """Generiert die TTL-Ausgabe basierend auf generate_all_forms()."""

    interval_patterns = forms["interval_patterns"]
    rows = forms["row_forms"]

    p_pattern = interval_patterns["P"]
    i_pattern = interval_patterns["I"]
    r_pattern = interval_patterns["R"]
    ri_pattern = interval_patterns["RI"]

    prime_forms = rows["P"]
    inversion_forms = rows["I"]
    retrograde_forms = rows["R"]
    retrograde_inversion_forms = rows["RI"]

    output = []
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
        # Master-Funktion: erzeugt alles
        forms = generate_all_forms(interval_pattern)

        # Intervall-Transformationen anzeigen
        print("\nIntervallmuster-Transformationen:")
        for key, value in forms["interval_patterns"].items():
            print(f"{key}:  {value}")

        # TTL-Ausgabe generieren
        ttl_output = generate_ttl_output(interval_pattern, forms)

        print("\n" + "=" * 50)
        print("TTL-AUSGABE:")
        print("=" * 50)
        print(ttl_output)

    except Exception as e:
        print(f"Fehler: {e}")
        print("Stellen Sie sicher, dass das Intervallmuster im Format '1_2_3_4_5_6_7_8_9_10_11' eingegeben wurde.")


if __name__ == "__main__":
    main()
