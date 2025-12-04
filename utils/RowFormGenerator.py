# last updated: 2025-12-04
# Twelve-Tone Row Form Generator (korrigiert: IP-Zuordnung aus Row-Intervallen)
# Wichtig: jede RowForm bekommt ihr IntervalPattern aus den tatsächlichen Pitch-Differenzen.

def invert_intervals(intervals):
    return [(12 - x) % 12 for x in intervals]

def reverse_intervals(intervals):
    return list(reversed(intervals))

def generate_rows_from_interval_pattern(interval_list):
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
    base_P0 = [int(x) for x in interval_pattern_str.split('_')]

    P0 = base_P0
    I0 = invert_intervals(P0)
    R0 = reverse_intervals(P0)
    RI0 = reverse_intervals(I0)

    originals = {"P": P0, "I": I0, "R": R0, "RI": RI0}

    sorted_items = sorted(originals.items(), key=lambda it: it[1])
    smallest_old_label, smallest_pattern = sorted_items[0]

    new_P = list(smallest_pattern)
    new_I = invert_intervals(new_P)
    new_R = reverse_intervals(new_P)
    new_RI = reverse_intervals(new_I)

    normalized = {"P": new_P, "I": new_I, "R": new_R, "RI": new_RI}

    prime_forms = generate_rows_from_interval_pattern(new_P)
    inversion_interval_list = [(-x) % 12 for x in new_P]
    inversion_forms = generate_rows_from_interval_pattern(inversion_interval_list)
    retrograde_forms = [list(reversed(r)) for r in prime_forms]
    retrograde_inversion_forms = [list(reversed(r)) for r in inversion_forms]

    row_forms = {"P": prime_forms, "I": inversion_forms, "R": retrograde_forms, "RI": retrograde_inversion_forms}

    norm_to_label = {tuple(v): k for k, v in normalized.items()}
    mapping_old_to_new = {old: norm_to_label.get(tuple(p), None) for old, p in originals.items()}

    normalized_str = {k: intervals_to_str(v) for k, v in normalized.items()}

    return {
        "originals": {k: intervals_to_str(v) for k, v in originals.items()},
        "normalized_intervals": normalized_str,
        "row_forms": row_forms,
        "mapping": mapping_old_to_new
    }

def format_row_name(row):
    return '_'.join(str(x) for x in row)

def _list_suffix(index, last_index, final_dot=False):
    if index < last_index:
        return ","
    else:
        return " ." if final_dot else " ,"

def row_to_intervals(row):
    """Berechnet Intervallfolge (Differenzen) aus einer Row (Liste von Pitch-Klassen)."""
    iv = [ (row[i+1] - row[i]) % 12 for i in range(len(row)-1) ]
    return iv

def generate_ttl_output_from_forms(forms):
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
    output.append("## Intervallmuster")
    output.append(f"## P: {p_pattern}")
    output.append(f"## I: {i_pattern}")
    output.append(f"## R: {r_pattern}")
    output.append(f"## RI: {ri_pattern}")
    output.append(f"mhg:rc_{p_pattern} a mhg:rowClass ;")
    output.append(f"    mhg:hasIntervalPattern mhg:ip_{p_pattern} ; # P")
    output.append(f"    mhg:hasIntervalPattern mhg:ip_{i_pattern} ; # I")
    output.append(f"    mhg:hasIntervalPattern mhg:ip_{r_pattern} ; # R")
    output.append(f"    mhg:hasIntervalPattern mhg:ip_{ri_pattern} ; # RI")
    output.append("    mhg:hasRowForm")

    # Listen in der rowClass
    output.append("        # P-Forms")
    last_idx = len(prime_forms) - 1
    for i, row in enumerate(prime_forms):
        suffix = _list_suffix(i, last_idx, final_dot=False)
        output.append(f"        mhg:rf_{format_row_name(row)}{suffix}")

    output.append("\n        # I-Forms")
    last_idx = len(inversion_forms) - 1
    for i, row in enumerate(inversion_forms):
        suffix = _list_suffix(i, last_idx, final_dot=False)
        output.append(f"        mhg:rf_{format_row_name(row)}{suffix}")

    output.append("\n        # R-Forms")
    last_idx = len(retrograde_forms) - 1
    for i, row in enumerate(retrograde_forms):
        suffix = _list_suffix(i, last_idx, final_dot=False)
        output.append(f"        mhg:rf_{format_row_name(row)}{suffix}")

    output.append("\n        # RI-Forms")
    last_idx = len(retrograde_inversion_forms) - 1
    for i, row in enumerate(retrograde_inversion_forms):
        suffix = _list_suffix(i, last_idx, final_dot=True)
        output.append(f"        mhg:rf_{format_row_name(row)}{suffix}")

    # Intervallmuster-Deklarationen
    output.append("\n# Intervallmuster-Deklarationen")
    for label in ["P", "I", "R", "RI"]:
        pattern_str = patterns[label]
        output.append(f"mhg:ip_{pattern_str} a mhg:intervalPattern ;")
        output.append(f"    mhg:hasRowClass mhg:rc_{p_pattern} .")

    # RowForm-Deklarationen: robust durch Intervall-Extraktion aus der Row selbst
    output.append("\n# RowForm-Deklarationen")

    # Erzeuge rowname -> ip, basierend auf tatsächlichen Row-Intervallen
    rowname_to_ip = {}
    for label in ["P", "I", "R", "RI"]:
        for row in rows[label]:
            rowname = format_row_name(row)
            iv = row_to_intervals(row)              # Intervalle direkt aus der Row
            ip_str = intervals_to_str(iv)
            rowname_to_ip[rowname] = ip_str

    emitted = set()
    # Ausgabe in stabiler Reihenfolge (P, I, R, RI)
    for label in ["P", "I", "R", "RI"]:
        for row in rows[label]:
            rowname = format_row_name(row)
            if rowname in emitted:
                continue
            emitted.add(rowname)
            ip_for_row = rowname_to_ip.get(rowname, p_pattern)
            output.append(f"mhg:rf_{rowname} a mhg:rowForm ;")
            output.append(f"    mhg:hasIntervalPattern mhg:ip_{ip_for_row} ;")
            output.append(f"    mhg:hasRowClass mhg:rc_{p_pattern} .")

    return "\n".join(output)

def parse_user_input(user_input):
    """
    Erlaubt ausschließlich Eingaben mit explizitem Prefix:
    - ip_<pattern>
    - rf_<row>
    
    Alles andere führt zu einer Fehlermeldung.
    """
    s = user_input.strip()

    if s.startswith("ip_"):
        pattern_str = s[3:]  # "ip_2_4_6" → "2_4_6"
        return pattern_str

    elif s.startswith("rf_"):
        row_str = s[3:]      # "rf_0_2_6_9" → "0_2_6_9"
        try:
            row = [int(x) for x in row_str.split("_")]
        except:
            raise ValueError("Ungültiges RowForm-Format nach 'rf_'. Erwartet: rf_0_2_6_9 ...")
        
        if len(row) < 2:
            raise ValueError("RowForm muss mindestens zwei Tonhöhen enthalten.")
        
        intervals = row_to_intervals(row)
        return intervals_to_str(intervals)

    else:
        raise ValueError(
            "Ungültige Eingabe. Einzugeben ist entweder:\n"
            "  ip_<intervallpattern>  (z.B. ip_2_4_3)\n"
            "oder\n"
            "  rf_<rowform>           (z.B. rf_0_2_6_9)\n"
            "Eingaben ohne 'ip_' oder 'rf_' werden nicht akzeptiert."
        )

def main():
    example = "rf_0_2_1_4_3_7 oder ip_2_11_3_11_4"
    print("Twelve-Tone Row Forms Generator (korrigierte IP-Zuordnung)")
    user_input = input(f"Reihenform oder Intervallmuster eingeben (Beispiel '{example}') + Return: ").strip()
    if user_input:
        pattern = parse_user_input(user_input)
    else:
        print("Bitte Eingabe mit ip_ oder rf_.")
        return

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
