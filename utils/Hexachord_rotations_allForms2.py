# hexachord_rdf_export.py
# Erzeugt Turtle (RDF) für Hexachord-Rotationen 1..6 mit Tn/TnI/Retrogrades
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
# RDF/Turtle helper
# -------------------------
def qname_for_rowform(row: List[int]) -> str:
    """Erzeuge QName wie mhg:0_2_4_5_8_10 (Achtung: beginnt mit Zahl, wie vom Nutzer gewünscht)."""
    return "mhg:" + fmt(row)

def triple_rowclass_hasRowForms_block(hex_rowclass: List[int], forms_groups: dict) -> str:
    """
    Erzeugt einen Turtle-Block:
    mhg:<rowClass> a mhg:rowClass ;
        mhg:hasRowForm
       # P
       mhg:... ,
       mhg:... ;
    .
    forms_groups: dict mit keys 'P','I','R','RI' -> list of row-lists
    """
    subj = "mhg:" + fmt(hex_rowclass)
    lines = []
    lines.append(f"{subj} a mhg:rowClass ;")
    lines.append("    mhg:hasRowForm")
    # P (Prime forms)
    # We will format each list as comma separated qnames, and keep groups separated by newlines and comments
    all_lines = []
    # Helper to convert row -> qname
    def q(r): return "mhg:" + fmt(r)
    # P
    p_list = forms_groups.get("P", [])
    if p_list:
        lines.append("   # P")
        for i, r in enumerate(p_list):
            comma = "," if i < len(p_list)-1 or any(forms_groups.get(k) for k in ("I","R","RI")) else ""
            lines.append(f"   {q(r)}{comma}")
    # I
    i_list = forms_groups.get("I", [])
    if i_list:
        # If P was present and last printed did not add comma, ensure comma separation is correct.
        # To keep Turtle valid, above approach prints each triple line; we'll join with newline and then ensure final termination with '.' later.
        lines.append("   # I")
        for i, r in enumerate(i_list):
            comma = "," if i < len(i_list)-1 or any(forms_groups.get(k) for k in ("R","RI")) else ""
            lines.append(f"   {q(r)}{comma}")
    # R
    r_list = forms_groups.get("R", [])
    if r_list:
        lines.append("   # R")
        for i, r in enumerate(r_list):
            comma = "," if i < len(r_list)-1 or any(forms_groups.get(k) for k in ("RI",)) else ""
            lines.append(f"   {q(r)}{comma}")
    # RI
    ri_list = forms_groups.get("RI", [])
    if ri_list:
        lines.append("   # RI")
        for i, r in enumerate(ri_list):
            comma = "," if i < len(ri_list)-1 else ""
            lines.append(f"   {q(r)}{comma}")
    # End block with a period. Ensure last printed line ends without trailing comma.
    # If the last line has a trailing comma it's allowed in Turtle? No — we must ensure the last item has no comma.
    # Our above logic tries to avoid comma on last element.
    # Append terminating semicolon? In structure we used 'a mhg:rowClass ;' then 'mhg:hasRowForm ...' so we must end with '.' 
    lines.append("   .")
    return "\n".join(lines)

# -------------------------
# Main generator
# -------------------------
def generate_turtle_for_pattern(interval_pattern_str: str, mod: int = 12, start_pc: int = 0) -> str:
    intervals = parse_pattern(interval_pattern_str)
    # sanity
    if len(intervals) != mod - 1:
        print(f"⚠️ Warnung: Erwartet {mod-1} Intervalle (für {mod} Töne). Eingabe hat {len(intervals)} Intervalle.")
    prototype = proto_row_from_intervals(intervals, start_pc=start_pc, mod=mod)

    turtle_lines = []
    # Prefixes
    turtle_lines.append("@prefix mhg: <http://example.org/mhg#> .")
    turtle_lines.append("@prefix : <http://example.org/> .")
    turtle_lines.append("")  # blank line

    # Human-readable comment header
    turtle_lines.append(f"# Generated hexachord rotations RDF for input rowClass: {interval_pattern_str}")
    turtle_lines.append(f"# Prototype rowForm (T0): {fmt(prototype)}")
    turtle_lines.append("") 

    for k in range(6):
        A_rot, B_rot, full_row = rotate_hexachords_independently(prototype, k)
        rowclass = intervals_from_rowform(full_row, mod=mod)

        # Header comment for this rotation
        turtle_lines.append(f"#" + "-"*100)
        turtle_lines.append(f"# HEXACHORD ROTATION {k+1}")
        turtle_lines.append(f"# RowForm:  {fmt(full_row)}")
        turtle_lines.append(f"# RowClass: {fmt(rowclass)}")
        turtle_lines.append("")  # blank

        # Add statements for RowForm and RowClass as plain comments/triples for readability
        # (These are comments; the RDF blocks below will represent the hexachord rowClasses)
        turtle_lines.append(f"# A-Hexachord: {fmt(A_rot)}")
        turtle_lines.append(f"# B-Hexachord: {fmt(B_rot)}")
        turtle_lines.append("") 

        # For A-hexachord: compute Tn, TnI, R(Tn), R(TnI)
        A_P = [ transpose_row(A_rot, n, mod=mod) for n in range(mod) ]
        A_I = [ transpose_inversion(A_rot, n, mod=mod) for n in range(mod) ]
        A_R = [ retrograde(r) for r in A_P ]
        A_RI = [ retrograde(r) for r in A_I ]

        forms_A = {
            "P": A_P,
            "I": A_I,
            "R": A_R,
            "RI": A_RI
        }

        # For B-hexachord:
        B_P = [ transpose_row(B_rot, n, mod=mod) for n in range(mod) ]
        B_I = [ transpose_inversion(B_rot, n, mod=mod) for n in range(mod) ]
        B_R = [ retrograde(r) for r in B_P ]
        B_RI = [ retrograde(r) for r in B_I ]

        forms_B = {
            "P": B_P,
            "I": B_I,
            "R": B_R,
            "RI": B_RI
        }

        # Create Turtle blocks using the hexachord rowClass as subject (exactly mhg:<rowClass> as requested)
        turtle_lines.append(triple_rowclass_hasRowForms_block(A_rot, forms_A))
        turtle_lines.append("")  # blank
        turtle_lines.append(triple_rowclass_hasRowForms_block(B_rot, forms_B))
        turtle_lines.append("")  # blank

    return "\n".join(turtle_lines)

# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    # Beispiel-Input (ersetze durch dein Muster)
    input_pattern = "2_2_1_3_2_8_1_2_2_2_2"  # Beispiel aus deiner Ausgabe-Anforderung
    turtle = generate_turtle_for_pattern(input_pattern, mod=12, start_pc=0)
    print(turtle)
