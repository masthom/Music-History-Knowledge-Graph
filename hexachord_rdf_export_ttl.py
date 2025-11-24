# hexachord_rdf_export_ttl.py
# Erweiterte Version: erzeugt zusätzlich inverse Tripel für alle RowForms.
# Außerdem: Abschluss-Punkt auf derselben Zeile.

from typing import List

# -------------------------
# Hilfsfunktionen
# -------------------------
def parse_pattern(s: str) -> List[int]:
    return [int(x) for x in s.strip().split("_") if x != ""]

def fmt(seq: List[int]) -> str:
    return "_".join(str(x) for x in seq)

def proto_row_from_intervals(intervals: List[int], start_pc: int = 0, mod: int = 12) -> List[int]:
    pcs = [start_pc % mod]
    for iv in intervals:
        pcs.append((pcs[-1] + iv) % mod)
    return pcs

def rotate_list_left(seq: List[int], k: int) -> List[int]:
    if len(seq) == 0:
        return []
    k = k % len(seq)
    return seq[k:] + seq[:k]

def rotate_hexachords_independently(row: List[int], k: int):
    A = row[:6]
    B = row[6:]
    A_rot = rotate_list_left(A, k)
    B_rot = rotate_list_left(B, k)
    return A_rot, B_rot, A_rot + B_rot

def intervals_from_rowform(row: List[int], mod: int = 12) -> List[int]:
    return [ (row[i+1] - row[i]) % mod for i in range(len(row)-1) ]

# Tn / TnI / Retrograde
def transpose_row(row: List[int], n: int, mod: int = 12) -> List[int]:
    return [ (x + n) % mod for x in row ]

def invert_row(row: List[int], mod: int = 12) -> List[int]:
    return [ (-x) % mod for x in row ]

def transpose_inversion(row: List[int], n: int, mod: int = 12) -> List[int]:
    inv = invert_row(row, mod=mod)
    return [ (x + n) % mod for x in inv ]

def retrograde(row: List[int]) -> List[int]:
    return list(reversed(row))

# -------------------------
# Turtle / TTL builder
# -------------------------
def qname(row: List[int]) -> str:
    return "mhg:" + fmt(row)

def block_rowclass_hasRowForms(rowclass_intervals: List[int],
                               groups_ordered: List[tuple]) -> str:
    """
    Erzeugt:
      - den rowClass-Block
      - die dazugehörigen inversen rowForm-Blöcke
    """
    subj = "mhg:" + fmt(rowclass_intervals)

    # Alle RowForms sammeln
    all_items = []
    for _, rows in groups_ordered:
        all_items.extend(rows)
    total = len(all_items)

    # ---------------------------
    # Haupt-Block (rowClass)
    # ---------------------------
    lines = []
    lines.append(f"{subj} a mhg:rowClass ;")
    lines.append("    mhg:hasRowForm")

    printed = 0
    for group_label, rows in groups_ordered:
        if not rows:
            continue
        lines.append(f"   # {group_label}")
        for r in rows:
            printed += 1
            comma = "," if printed < total else ""
            lines.append(f"   {qname(r)}{comma}")
    lines.append("   .")  # Punkt auf derselben Zeile

    # ---------------------------
    # Inverse Tripel (rowForms)
    # ---------------------------
    inverse_blocks = []
    for r in all_items:
        inv = []
        inv.append(f"{qname(r)} a mhg:rowForm ;")
        inv.append(f"    mhg:hasRowClass {subj} .")
        inverse_blocks.append("\n".join(inv))

    return "\n".join(lines) + "\n\n" + "\n\n".join(inverse_blocks)


# -------------------------
# Main generator
# -------------------------
def generate_turtle_for_pattern_to_file(interval_pattern_str: str,
                                        out_filename: str = "hexachord_rotations.ttl",
                                        mod: int = 12,
                                        start_pc: int = 0):

    intervals = parse_pattern(interval_pattern_str)
    prototype = proto_row_from_intervals(intervals, start_pc=start_pc, mod=mod)

    turtle_lines = []
    turtle_lines.append("@prefix mhg: <http://example.org/mhg#> .")
    turtle_lines.append("@prefix : <http://example.org/> .")
    turtle_lines.append("")

    turtle_lines.append(f"# Generated RDF for rowClass: {interval_pattern_str}")
    turtle_lines.append(f"# T0 rowForm: {fmt(prototype)}\n")

    for k in range(6):
        A_rot, B_rot, full_row = rotate_hexachords_independently(prototype, k)
        rowclass = intervals_from_rowform(full_row, mod=mod)

        turtle_lines.append("#" + "-"*100)
        turtle_lines.append(f"# HEXACHORD ROTATION {k+1}")
        turtle_lines.append(f"# RowForm:  {fmt(full_row)}")
        turtle_lines.append(f"# RowClass: {fmt(rowclass)}\n")
        turtle_lines.append(f"# A-Hexachord: {fmt(A_rot)}")
        turtle_lines.append(f"# B-Hexachord: {fmt(B_rot)}\n")

        # A-Gruppen
        A_P  = [ transpose_row(A_rot, n, mod=mod) for n in range(mod) ]
        A_I  = [ transpose_inversion(A_rot, n, mod=mod) for n in range(mod) ]
        A_R  = [ retrograde(r) for r in A_P ]
        A_RI = [ retrograde(r) for r in A_I ]
        groups_A = [("P", A_P), ("I", A_I), ("R", A_R), ("RI", A_RI)]

        # B-Gruppen
        B_P  = [ transpose_row(B_rot, n, mod=mod) for n in range(mod) ]
        B_I  = [ transpose_inversion(B_rot, n, mod=mod) for n in range(mod) ]
        B_R  = [ retrograde(r) for r in B_P ]
        B_RI = [ retrograde(r) for r in B_I ]
        groups_B = [("P", B_P), ("I", B_I), ("R", B_R), ("RI", B_RI)]

        # rowClass A/B berechnen
        A_rowclass = intervals_from_rowform(A_rot, mod=mod)
        B_rowclass = intervals_from_rowform(B_rot, mod=mod)

        # A Block + inverse Tripel
        blockA = block_rowclass_hasRowForms(A_rowclass, groups_A)
        turtle_lines.append(blockA)
        turtle_lines.append("")

        # B Block + inverse Tripel
        blockB = block_rowclass_hasRowForms(B_rowclass, groups_B)
        turtle_lines.append(blockB)
        turtle_lines.append("")

    # Schreiben
    text = "\n".join(turtle_lines)
    with open(out_filename, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"TTL written to: {out_filename}")


# -------------------------
# Beispiel
# -------------------------
if __name__ == "__main__":
    input_pattern = "2_2_1_3_2_8_1_2_2_2_2"
    out_file = "hexachord_rotations.ttl"
    generate_turtle_for_pattern_to_file(input_pattern, out_filename=out_file)
