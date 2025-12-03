# Twelve-Tone Row Form Generator (mit automatischer Normalisierung der Intervallmuster)

def compute_interval_transformations(intervals):
    """Berechnet P, I, R, RI als Listen von Integern."""
    P = intervals
    I = [(12 - x) % 12 for x in intervals]
    R = list(reversed(P))
    RI = list(reversed(I))
    return {"P": P, "I": I, "R": R, "RI": RI}


def find_normalized_order(patterns):
    """
    Bestimmt, welches Intervallmuster lexikographisch das kleinste ist,
    und ordnet P/I/R/RI entsprechend neu.
    """
    # Sortiert nach Wert der Listen (lexikographisch)
    ordered = sorted(patterns.items(), key=lambda item: item[1])

    # Das kleinste wird die neue P-Form
    new_order_labels = ["P", "I", "R", "RI"]
    mapping = {old_label: new_label for (new_label, (old_label, _)) in zip(new_order_labels, ordered)}

    # Mapping invertieren: neue_label = mapping_von_altem_label
    new_patterns = {mapping[old]: values for old, values in patterns.items()}

    return new_patterns, mapping


def generate_rows_from_intervals(interval_list):
    """Erzeugt 12 Reihenformen (Startnoten 0–11) eines Intervallmusters."""
    rows = []
    for start_note in range(12):
        row = [start_note]
        current = start_note
        for iv in interval_list:
            current = (current + iv) % 12
            row.append(current)
        rows.append(row)
    return rows


def generate_all_forms(interval_pattern):
    """
    1. Berechnet alle vier Intervallmuster (P, I, R, RI)
    2. Normalisiert sie (das kleinste => neue P)
    3. Erzeugt passende RowForms
    """
    # Originalmuster
    intervals = [int(x) for x in interval_pattern.split('_')]

    # 1. Intervalltransformationen berechnen
    interval_patterns = compute_interval_transformations(intervals)

    # 2. Normalisieren: kleinstes Muster => neue P-Form
    normalized_intervals, mapping = find_normalized_order(interval_patterns)

    # 3. RowForms auf Grundlage der neu zugewiesenen Intervallmuster
    row_forms = {
        form: generate_rows_from_intervals(iv_list)
        for form, iv_list in normalized_intervals.items()
    }

    # Als Strings für Ausgabe/TTL aufbereiten
    interval_patterns_str = {
        form: "_".join(str(x) for x in iv_list) for form, iv_list in normalized_intervals.items()
    }

    return {
        "interval_patterns": interval_patterns_str,
        "row_forms": row_forms,
        "mapping": mapping  # optional: zeigt, welches ursprüngliche Muster wohin gewandert ist
    }


def format_row_name(row):
    return '_'.join(str(note) for note in row)


def generate_ttl_output(interval_pattern, forms):
    patterns = forms["interval_patterns"]
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
    output.append(f"# Normalisierte Intervallmuster")
    output.append(f"# P: {p_pattern}")
    output.append(f"# I: {i_pattern}")
    output.append(f"# R: {r_pattern}")
    output.append(f"# RI: {ri_pattern}")
    output.append(f"mhg:{p_pattern} a mhg:rowClass ;")
    output.append("    mhg:hasRowForm")

    # P
    output.append("        # P-Forms (0-11)")
    for i, row in enumerate(prime_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # I
    output.append("        \n        # I-Forms (0-11)")
    for i, row in enumerate(inversion_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # R
    output.append("        \n        # R-Forms (0-11)")
    for i, row in enumerate(retrograde_forms):
        suffix = "," if i < 11 else " ,"
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # RI
    output.append("        \n        # RI-Forms (0-11)")
    for i, row in enumerate(retrograde_inversion_forms):
        suffix = "," if i < 11 else " ."
        output.append(f"        mhg:{format_row_name(row)}{suffix}")

    # Deklarationen
    output.append("\n# RowForm-Deklarationen")
    for row in prime_forms + inversion_forms + retrograde_forms + retrograde_inversion_forms:
        name = format_row_name(row)
        output.append(f"mhg:{name} a mhg:rowForm ; mhg:hasRowClass mhg:{p_pattern} .")

    return "\n".join(output)


def main():
    interval_pattern = "1_3_1_6_11_5_4_2_9_2_6"

    print("Twelve-Tone Row Forms Generator mit P-Normalisierung")
    print("===================================================")

    user_input = input(f"Intervallmuster eingeben (Enter für Beispiel '{interval_pattern}'): ").strip()
    if user_input:
        interval_pattern = user_input

    try:
        forms = generate_all_forms(interval_pattern)

        print("\nNormalisierte Intervallmuster:")
        for form, patt in forms["interval_patterns"].items():
            print(f"{form}: {patt}")

        print("\nMapping (ursprünglich → neu):")
        for old, new in forms["mapping"].items():
            print(f"{old} → {new}")

        ttl_output = generate_ttl_output(interval_pattern, forms)

        print("\n" + "=" * 50)
        print("TTL-AUSGABE:")
        print("=" * 50)
        print(ttl_output)

    except Exception as e:
        print("Fehler:", e)
        print("Bitte ein korrektes Intervallmuster eingeben, z. B. 1_2_3_4_5_6_7_8_9_10_11.")


if __name__ == "__main__":
    main()
