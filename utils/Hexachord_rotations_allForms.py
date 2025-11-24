# hexachord_rotations_with_Tn_TnI.py

def parse_pattern(s: str):
    return [int(x) for x in s.strip().split("_") if x]


def proto_row_from_intervals(intervals, start_pc=0, mod=12):
    pcs = [start_pc % mod]
    for iv in intervals:
        pcs.append((pcs[-1] + iv) % mod)
    return pcs


def rotate_list_left(seq, k):
    k = k % len(seq)
    return seq[k:] + seq[:k]


def rotate_hexachords_independently(row, k):
    A = row[:6]
    B = row[6:]
    A_rot = rotate_list_left(A, k)
    B_rot = rotate_list_left(B, k)
    return A_rot, B_rot, A_rot + B_rot


def intervals_from_rowform(row, mod=12):
    return [(row[i+1] - row[i]) % mod for i in range(len(row)-1)]


# ----------------------------------------
# Tn / TnI / Retrograde for a 6-tone list
# ----------------------------------------
def transpose_row(row, n, mod=12):
    return [(x + n) % mod for x in row]


def invert_row(row, mod=12):
    return [(-x) % mod for x in row]


def transpose_inversion(row, n, mod=12):
    inv = invert_row(row, mod=mod)
    return [(x + n) % mod for x in inv]


def retrograde(row):
    return list(reversed(row))


# ----------------------------------------
# Build full structure with Tn/TnI per hexachord
# ----------------------------------------
def compute_hexachord_transformations(h, mod=12):
    """
    For a hexachord h = [p1..p6], return:
      - Tn
      - TnI
      - Retrograde(Tn)
      - Retrograde(TnI)
    """
    Tn = []
    TnI = []
    R_Tn = []
    R_TnI = []

    for n in range(mod):
        row_Tn = transpose_row(h, n, mod)
        row_TnI = transpose_inversion(h, n, mod)
        Tn.append((n, row_Tn))
        TnI.append((n, row_TnI))
        R_Tn.append((n, retrograde(row_Tn)))
        R_TnI.append((n, retrograde(row_TnI)))

    return {
        "Tn": Tn,
        "TnI": TnI,
        "Retro_Tn": R_Tn,
        "Retro_TnI": R_TnI
    }


# --------------------------------------------------------
# Main: Hexachord rotations 1–6 + Tn/TnI for each hexachord
# --------------------------------------------------------
def generate_hexachord_rotations(interval_pattern_str, mod=12, start_pc=0):
    intervals = parse_pattern(interval_pattern_str)
    base_row = proto_row_from_intervals(intervals, start_pc=start_pc, mod=mod)

    rotations = []

    for k in range(6):  # Hexachord rotations 1–6
        A_rot, B_rot, full_row = rotate_hexachords_independently(base_row, k)
        rowClass = intervals_from_rowform(full_row, mod)

        A_trans = compute_hexachord_transformations(A_rot, mod)
        B_trans = compute_hexachord_transformations(B_rot, mod)

        rotations.append({
            "rotation_index": k + 1,
            "A_hexachord": A_rot,
            "B_hexachord": B_rot,
            "rowForm": full_row,
            "rowClass": rowClass,

            # Tn/TnI sets:
            "A_transformations": A_trans,
            "B_transformations": B_trans
        })

    return {
        "input_rowClass": interval_pattern_str,
        "prototype_rowForm": base_row,
        "rotations": rotations
    }


# --------------------------------------------------------
# Output formatting
# --------------------------------------------------------
def fmt(row): return "_".join(str(x) for x in row)


def print_hexachord_rotations(data):
    print("="*100)
    print("Input rowClass:        ", data["input_rowClass"])
    print("Prototype rowForm T0:  ", fmt(data["prototype_rowForm"]))
    print("="*100)

    for rot in data["rotations"]:
        print()
        print(f"HEXACHORD ROTATION {rot['rotation_index']}")
        print("-"*100)
        print(" RowForm:  ", fmt(rot["rowForm"]))
        print(" RowClass: ", fmt(rot["rowClass"]))

        print("\nA-Hexachord:", fmt(rot["A_hexachord"]))
        print("B-Hexachord:", fmt(rot["B_hexachord"]))

        print("\n=== Transformations A ===")
        for n, seq in rot["A_transformations"]["Tn"]:
            print(f"T{n}:   {fmt(seq)}")
        print()
        for n, seq in rot["A_transformations"]["TnI"]:
            print(f"T{n}I:  {fmt(seq)}")
        print()
        for n, seq in rot["A_transformations"]["Retro_Tn"]:
            print(f"R(T{n}):   {fmt(seq)}")
        print()
        for n, seq in rot["A_transformations"]["Retro_TnI"]:
            print(f"R(T{n}I):  {fmt(seq)}")

        print("\n=== Transformations B ===")
        for n, seq in rot["B_transformations"]["Tn"]:
            print(f"T{n}:   {fmt(seq)}")
        print()
        for n, seq in rot["B_transformations"]["TnI"]:
            print(f"T{n}I:  {fmt(seq)}")
        print()
        for n, seq in rot["B_transformations"]["Retro_Tn"]:
            print(f"R(T{n}):   {fmt(seq)}")
        print()
        for n, seq in rot["B_transformations"]["Retro_TnI"]:
            print(f"R(T{n}I):  {fmt(seq)}")

        print("-"*100)


# --------------------------------------------------------
# Example run
# --------------------------------------------------------
if __name__ == "__main__":
    pattern = "2_2_1_3_2_8_1_2_2_2_2"
    data = generate_hexachord_rotations(pattern)
    print_hexachord_rotations(data)
