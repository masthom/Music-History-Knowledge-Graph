import re


def compute_intervals(rf_pattern):
    nums = list(map(int, rf_pattern.split('_')))
    intervals = [(nums[i+1] - nums[i]) % 12 for i in range(len(nums) - 1)]
    return "_".join(map(str, intervals))


def integrate_intervalpatterns(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []

    # RowForm-Start erkennen
    rf_start_re = re.compile(
        r"^\s*(mhg:rf_([0-9_]+))\s+a\s+mhg:rowForm\b"
    )

    for line in lines:
        m = rf_start_re.match(line)

        if not m:
            new_lines.append(line)
            continue

        # ------------------------------------
        # rowForm erkannt
        # ------------------------------------
        full_rf = m.group(1)     # z.B. mhg:rf_1_2_3_4
        pattern_only = m.group(2)  # z.B. 1_2_3_4

        ip = compute_intervals(pattern_only)
        ip_uri = f"mhg:ip_{ip}"

        # Falls bereits hasIntervalPattern in der selben Zeile ist → nichts tun
        if "hasIntervalPattern" in line:
            new_lines.append(line)
            continue

        # Wir müssen das Semikolon NACH rowForm ; finden
        # Damit die Einfügung _sofort danach_ erfolgt
        pos = line.find(";")
        if pos == -1:
            # Falls ausnahmsweise kein ; existiert → normal anhängen
            new_lines.append(line.rstrip() + f"; mhg:hasIntervalPattern {ip_uri} ;\n")
            continue

        # Einrückung berechnen (Whitespace vor „mhg:rf…“)
        indent_match = re.match(r"^(\s*)", line)
        indent = indent_match.group(1)

        # Neue Einfügezeile erzeugen
        insert_line = f"{indent}    mhg:hasIntervalPattern {ip_uri} ;\n"

        # Zeile aufsplitten: vor dem Semikolon, Semikolon + Reste, neue Zeile einfügen
        before = line[:pos+1] + "\n"
        after = line[pos+1:].lstrip()

        if after:
            # Es gab weitere Properties in derselben Zeile → neue Zeile einfügen
            new_lines.append(before)
            new_lines.append(insert_line)
            new_lines.append(indent + after)
        else:
            # Zeile endete direkt nach dem Semikolon
            new_lines.append(before)
            new_lines.append(insert_line)

    # speichern
    with open(output_path, "w", encoding="utf-8") as out:
        out.writelines(new_lines)

    print("Fertig. Neue Datei:", output_path)
    # ----------------------------------------------------
# Ausführung
# ----------------------------------------------------
if __name__ == "__main__":
    input_path = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
    output_path = "MusicHistoryGraph_TwelveToneMusic_WithRowFormIPs.ttl"
    integrate_intervalpatterns(input_path, output_path)
