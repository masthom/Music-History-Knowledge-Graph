# rowform_rotation_tool.py
from typing import List

def parse_pattern(s: str) -> List[int]:
    """Parse '1_2_3' -> [1,2,3]. Accepts whitespace."""
    if s is None or s.strip() == "":
        return []
    return [int(x) for x in s.strip().split("_") if x != ""]


def fmt(seq: List[int]) -> str:
    """Format list as 'a_b_c' (empty -> '')."""
    return "_".join(str(x) for x in seq)


def proto_row_from_intervals(intervals: List[int], start_pc: int = 0, mod: int = 12) -> List[int]:
    """
    Build a prototypical rowForm from an interval list.
    If intervals has length m, rowForm has length m+1.
    """
    pcs = [start_pc % mod]
    for iv in intervals:
        pcs.append((pcs[-1] + iv) % mod)
    return pcs


def rotate_rowform(row: List[int], shift: int = 1) -> List[int]:
    """Cyclic rotation (left shift) of the rowForm by 'shift' positions."""
    n = len(row)
    if n == 0:
        return []
    s = shift % n
    return row[s:] + row[:s]


def intervals_from_rowform(row: List[int], mod: int = 12) -> List[int]:
    """
    Compute interval pattern (rowClass) from a rowForm.
    Intervals are successive differences: row[i+1] - row[i] (mod).
    Length of result = len(row) - 1 (if row length >=1).
    """
    if len(row) <= 1:
        return []
    return [ (row[i+1] - row[i]) % mod for i in range(len(row) - 1) ]


def generate_rotations_and_rowclasses(interval_pattern_str: str, mod: int = 12, start_pc: int = 0):
    """
    Given interval_pattern_str like '1_10_3_...' which is rowClass of rotation 1,
    produce:
      - prototype rowForm (T0) starting at start_pc
      - for each rotation k (0..L-1): the rotated rowForm and its rowClass (intervals)
    Returns a list of dicts with keys:
      'rotation_index' (1-based, rotation of the rowForm),
      'rowForm' (list),
      'rowForm_str' (underscore string),
      'rowClass' (list of intervals),
      'rowClass_str' (underscore string)
    """
    intervals = parse_pattern(interval_pattern_str)
    if intervals == []:
        raise ValueError("Leeres Intervallmuster: bitte Intervalle als Unterstrich-String angeben.")
    proto = proto_row_from_intervals(intervals, start_pc=start_pc, mod=mod)
    L = len(proto)
    results = []

    # For all rotations of the rowForm (shift 0..L-1)
    for shift in range(L):
        rot_row = rotate_rowform(proto, shift)
        rot_rowclass = intervals_from_rowform(rot_row, mod=mod)
        results.append({
            "rotation_index": shift + 1,            # 1-based (Rotation 1 is original rowForm)
            "rowForm": rot_row,
            "rowForm_str": fmt(rot_row),
            "rowClass": rot_rowclass,
            "rowClass_str": fmt(rot_rowclass)
        })

    return {
        "input_rowClass_str": interval_pattern_str,
        "prototype_rowForm": proto,
        "prototype_rowForm_str": fmt(proto),
        "mod": mod,
        "results": results
    }


def print_report(data: dict):
    print("#" * 72)
    print("Input rowClass (Rotation 1):", data["input_rowClass_str"])
    print("Modulus:", data["mod"])
    print("Prototype rowForm (T0, start_pc=0):", data["prototype_rowForm_str"])
    print("#" * 72)
    for entry in data["results"]:
        print(f"Rotation {entry['rotation_index']}:")
        print(" rowForm:  ", entry["rowForm_str"])
        print(" rowClass: ", entry["rowClass_str"])
        # Optional checks:
        unique = len(set(entry["rowForm"])) == len(entry["rowForm"])
        if not unique:
            print(" ⚠️ Hinweis: rowForm enthält Duplikate (nicht alle pitch classes eindeutig).")
        print("-" * 72)


# ---------------------------
# Beispiel - direkt ausführbar
if __name__ == "__main__":
    # === Beispiel-Input ===
    # rowClass der Rotation 1 (Unterstrich-getrennt)
    input_pattern = "2_8_11_7_2_1_8_8_6_3_5"   # ersetze durch dein Muster

    # Modulus (standard 12 für Pitch Classes). Ändere, wenn du in anderem Modul arbeiten willst.
    mod = 12

    data = generate_rotations_and_rowclasses(input_pattern, mod=mod, start_pc=0)
    print_report(data)
