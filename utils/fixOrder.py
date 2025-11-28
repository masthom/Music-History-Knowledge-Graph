import re

# ---------------------------------------------------------------
# Hilfsfunktion zur numerischen Sortierung von mhg:rc_…
# ---------------------------------------------------------------

def rc_sort_key(rc_name: str):
    # extrahiert: mhg:rc_10_4_7 → [10, 4, 7]
    nums = rc_name.split("mhg:rc_")[1].split("_")
    return [int(n) for n in nums if n.isdigit()]


# ---------------------------------------------------------------
# Hauptfunktion: Blöcke extrahieren, sortieren, Leerzeilen einfügen
# ---------------------------------------------------------------

def reorder_rowclass_blocks(input_path, output_path):

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = []
    current_block = []
    recording = False

    # -----------------------------------------------------------
    # 1. Alle Blöcke ab "## Intervallmuster" erfassen
    # -----------------------------------------------------------
    for line in lines:
        if line.startswith("## Intervallmuster"):
            # neuen Block beginnen
            if current_block:
                blocks.append(current_block)
            current_block = [line]
            recording = True
        elif recording:
            current_block.append(line)

    # letzten Block sichern
    if current_block:
        blocks.append(current_block)

    # -----------------------------------------------------------
    # 2. RowClass extrahieren und zuordenbar machen
    # -----------------------------------------------------------
    rc_regex = re.compile(r"mhg:rc_[0-9_]+")
    block_map = {}  # rc_name → block

    for block in blocks:
        block_text = "".join(block)
        m = rc_regex.search(block_text)
        if not m:
            continue
        rc_name = m.group(0)
        block_map[rc_name] = block

    # -----------------------------------------------------------
    # 3. numerisch sortieren
    # -----------------------------------------------------------
    sorted_rcs = sorted(block_map.keys(), key=rc_sort_key)

    # -----------------------------------------------------------
    # 4. Leerzeile nach Ende der RowClass-Deklaration einfügen
    # -----------------------------------------------------------

    def insert_blank_line(block):

        out = []
        rowclass_finished = False

        for line in block:

            # Ende der RowClass-Deklaration: Zeile endet mit Punkt
            if not rowclass_finished and re.search(r'\.\s*$', line):
                rowclass_finished = True
                out.append(line)
                continue

            # erste echte ip-Zeile nach abgeschlossener RowClass
            if rowclass_finished is True and line.startswith("mhg:ip_"):
                # Leerzeile einfügen, sofern nicht vorhanden
                if len(out) > 0 and out[-1].strip() != "":
                    out.append("\n")
                out.append(line)
                # wir sind fertig mit dem Einfügen
                rowclass_finished = "done"
                continue

            out.append(line)

        return "".join(out)

    # -----------------------------------------------------------
    # 5. Datei neu erzeugen
    # -----------------------------------------------------------

    # Alles vor dem ersten Block wiederherstellen
    first_block_start_index = lines.index(blocks[0][0])

    with open(output_path, "w", encoding="utf-8") as f:

        f.writelines(lines[:first_block_start_index])

        for rc in sorted_rcs:
            processed = insert_blank_line(block_map[rc])
            f.write(processed)

    print("Fertig: numerisch sortiert + Leerzeilen korrekt gesetzt.")


# ---------------------------------------------------------------
# Skript direkt aufrufen
# ---------------------------------------------------------------

if __name__ == "__main__":
    input_path = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"
    output_path = "MusicHistoryGraph_TwelveToneMusic_Reordered.ttl"

    reorder_rowclass_blocks(input_path, output_path)
