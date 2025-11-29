import re

def compute_intervals(rf_pattern):
    nums = list(map(int, rf_pattern.split('_')))
    intervals = [(nums[i+1] - nums[i]) % 12 for i in range(len(nums) - 1)]
    return "_".join(map(str, intervals))


def integrate_intervalpatterns(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    n = len(lines)
    i = 0

    # robust: erlaubt beliebige Whitespaces, Kommentare, einzeilig oder mehrzeilig
    rf_start_re = re.compile(
        r"^\s*mhg:rf_(?P<pattern>[0-9_]+)\s+a\s+mhg:rowForm\b"
    )

    block_end_re = re.compile(r"\.\s*$")  # Punkt am Zeilenende

    while i < n:
        line = lines[i]
        m = rf_start_re.match(line)

        if not m:
            new_lines.append(line)
            i += 1
            continue

        # ------------------------------------
        # RowForm block erkannt
        # ------------------------------------
        rf_pattern = m.group("pattern")
        ip_pattern = compute_intervals(rf_pattern)
        ip_name = f"mhg:ip_{ip_pattern}"

        # Block sammeln
        block = [line]
        i += 1

        while i < n and not block_end_re.search(lines[i]):
            block.append(lines[i])
            i += 1

        # letzte Zeile mit "." einbeziehen
        if i < n:
            block.append(lines[i])
            i += 1

        # prüfen, ob hasIntervalPattern innerhalb des RowForm-Blocks existiert
        already = any("mhg:hasIntervalPattern" in l for l in block)

        if not already:
            # Einrückung der bestehenden Properties erkennen
            indent = "    "
            # wenn zweite Zeile existiert, dessen Einrückung übernehmen
            if len(block) > 1:
                m2 = re.match(r"^(\s*)", block[1])
                indent = m2.group(1)

            insert_line = f"{indent}mhg:hasIntervalPattern {ip_name} ;\n"

            # direkt VOR letzter Zeile mit "."
            block.insert(-1, insert_line)

        # Block zurückschreiben
        new_lines.extend(block)

    # Datei speichern
    with open(output_path, "w", encoding="utf-8") as out:
        out.writelines(new_lines)

    print("OK – neue Datei erzeugt:", output_path)


# ----------------------------------------------------
# Ausführung
# ----------------------------------------------------
if __name__ == "__main__":
    input_path = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
    output_path = "MusicHistoryGraph_TwelveToneMusic_WithRowFormIPs.ttl"
    integrate_intervalpatterns(input_path, output_path)
