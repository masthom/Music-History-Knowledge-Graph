# hexachord_rotations.py

def parse_pattern(s: str):
    """Parse interval pattern '1_10_3_...' into list of ints."""
    return [int(x) for x in s.strip().split("_") if x]


def proto_row_from_intervals(intervals, start_pc=0, mod=12):
    """Generate rowForm (T0) from interval pattern."""
    pcs = [start_pc % mod]
    for iv in intervals:
        pcs.append((pcs[-1] + iv) % mod)
    return pcs


def rotate_list_left(seq, k):
    k = k % len(seq)
    return seq[k:] + seq[:k]


def rotate_hexachords_independently(row, k):
    """
    Perform independent hexachord rotation for A(1–6) and B(7–12).
    Rotation index k: 
      k = 0 → Rotation 1 (identity)
      k = 1 → Rotation 2
      k = 2 → Rotation 3
      ...
      k = 5 → Rotation 6
    """
    A = row[:6]
    B = row[6:]
    A_rot = rotate_list_left(A, k)
    B_rot = rotate_list_left(B, k)
    return A_rot + B_rot


def intervals_from_rowform(row, mod=12):
    return [(row[i+1] - row[i]) % mod for i in range(len(row)-1)]


def generate_hexachord_rotations(interval_pattern_str, mod=12, start_pc=0):
    """
    Generate:
    - rotation 1 (k=0)
    - rotation 2 (k=1)
    - rotation 3 (k=2)
    - rotation 4 (k=3)
    - rotation 5 (k=4)
    - rotation 6 (k=5)
    
    Each rotation:
       - rowForm
       - new rowClass
    """
    intervals = parse_pattern(interval_pattern_str)
    base_row = proto_row_from_intervals(intervals, start_pc=start_pc, mod=mod)

    results = []

    for k in range(6):  # rotations 1–6
        rot_row = rotate_hexachords_independently(base_row, k)
        rot_rowclass = intervals_from_rowform(rot_row, mod=mod)

        results.append({
            "rotation_index": k + 1,
            "rowForm": rot_row,
            "rowForm_str": "_".join(map(str, rot_row)),
            "rowClass": rot_rowclass,
            "rowClass_str": "_".join(map(str, rot_rowclass)),
        })

    return {
        "input_rowClass": interval_pattern_str,
        "prototype_rowForm": "_".join(map(str, base_row)),
        "rotations": results
    }


def print_hexachord_rotations(data):
    print("=" * 80)
    print("Input rowClass:        ", data["input_rowClass"])
    print("Prototype rowForm T0:  ", data["prototype_rowForm"])
    print("=" * 80)

    for rot in data["rotations"]:
        print()
        print(f"Rotation {rot['rotation_index']}:")
        print(" rowForm:  ", rot["rowForm_str"])
        print(" rowClass: ", rot["rowClass_str"])
        print("-" * 80)


# -----------------------------
# Example use
# -----------------------------
if __name__ == "__main__":
    pattern = "2_2_1_3_2_8_1_2_2_2_2"
    data = generate_hexachord_rotations(pattern)
    print_hexachord_rotations(data)
