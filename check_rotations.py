import re
import sys
from itertools import combinations

######################################################################
# 1. Robustes Parsen der Intervallmuster-Blöcke
######################################################################

def parse_interval_blocks(ttl_text):
    """
    Extrahiert P, R, RI, I Intervallmuster-Blöcke aus Kommentarabschnitten.
    Rückgabe: Liste von Dicts: {
        'P': [...],
        'R': [...],
        'RI': [...],
        'I': [...],
        'all': [P,R,RI,I als Listen]
    }
    """
    blocks = []

    # Erlaubt:
    # ## Intervallmuster:
    # # P: 1_2_3...
    # #R: 1_2_3...
    block_start = re.compile(r"^\s*##\s*Intervallmuster", re.IGNORECASE)
    line_pattern = re.compile(r"^\s*#\s*(P|R|RI|I)\s*:\s*([0-9_]+)")

    lines = ttl_text.splitlines()
    i = 0
    while i < len(lines):
        if block_start.search(lines[i]):
            block = {}
            j = i + 1
            while j < len(lines):
                match = line_pattern.search(lines[j])
                if match:
                    label = match.group(1)
                    seq_str = match.group(2)
                    seq = list(map(int, seq_str.split("_")))
                    block[label] = seq
                elif lines[j].strip().startswith("## Intervallmuster"):
                    break
                elif lines[j].strip().startswith("#") is False:
                    # Ende des Blocks
                    break
                j += 1

            if "P" in block:
                # Manche Blöcke können unvollständig sein
                block["all"] = [block[k] for k in ("P","R","RI","I") if k in block]
                blocks.append(block)

            i = j
        else:
            i += 1

    return blocks


######################################################################
# 2. Zyklische Erweiterung eines Intervallmusters
######################################################################

def cyclic_interval(intervals):
    """
    Erzeugt das zyklisch komplette Intervallmuster:
    [i0, i1, ..., in-1, Δ(last→first)]
    Δ(last→first) wird modulo 12 berechnet.
    """
    if not intervals:
        return []

    last = intervals[-1]
    first = intervals[0]
    wrap = (first - last) % 12
    return intervals + [wrap]


######################################################################
# 3. Rotationsäquivalenz zweier Muster
######################################################################

def is_rotation(a, b):
    """
    Prüft, ob Liste b eine Rotation von Liste a ist.
    Return: (True, shift) oder (False, None)
    """
    if len(a) != len(b):
        return (False, None)

    doubled = a + a
    b_str = ",".join(map(str, b))
    doubled_str = ",".join(map(str, doubled))

    # Suche b als Substring
    pos = doubled_str.find(b_str)
    if pos == -1:
        return (False, None)

    # Position in Elementen statt Zeichen bestimmen:
    a_str = ",".join(map(str, a))
    el_len = len(a_str) + 1  # grobe Orientierung, genügt hier

    # genaue Rotation bestimmen
    for shift in range(len(a)):
        if a[shift:] + a[:shift] == b:
            return (True, shift)

    return (False, None)


######################################################################
# 4. Hauptalgorithmus: Vergleich aller zyklischen Muster
######################################################################

def detect_rotations(blocks):
    """
    Vergleicht alle zyklischen Intervallmuster der Blöcke gegeneinander.
    Gibt Liste von Matches zurück:
    {
       "seqA": [...],
       "seqB": [...],
       "shift": x,
       "labelA": "P/R/I/RI",
       "labelB": ...
    }
    """
    all_entries = []   # Jede einzelne (blockIndex, label, seq)
    for bi, block in enumerate(blocks):
        for label, seq in block.items():
            if label == "all":
                continue
            cyc = cyclic_interval(seq)
            all_entries.append((bi, label, seq, cyc))

    matches = []

    for (a_idx, a_label, a_raw, a_cyc), (b_idx, b_label, b_raw, b_cyc) in combinations(all_entries, 2):
        eq, shift = is_rotation(a_cyc, b_cyc)
        if eq:
            matches.append({
                "A_block": a_idx,
                "B_block": b_idx,
                "A_label": a_label,
                "B_label": b_label,
                "A_seq": a_raw,
                "B_seq": b_raw,
                "shift": shift
            })
    return matches


######################################################################
# 5. TTL-Ausgabe
######################################################################

def seq_to_iri(seq):
    return "mhg:" + "_".join(map(str, seq))

def write_ttl(matches, outpath="outputRotations.ttl"):
    with open(outpath, "w", encoding="utf8") as f:
        for m in matches:
            iriA = seq_to_iri(m["A_seq"])
            iriB = seq_to_iri(m["B_seq"])

            f.write(f"{iriA} mhg:isRotationOf {iriB} ;\n")
            f.write(f'    mhg:rotationShift "Rotation {m["shift"]}" .\n\n')

            f.write(f"{iriB} mhg:isRotationOf {iriA} ;\n")
            f.write(f'    mhg:rotationShift "Rotation {m["shift"]}" .\n\n')

    print(f"Wrote {len(matches)} matches → {outpath}")


######################################################################
# MAIN
######################################################################

def main(ttlfile):
    text = open(ttlfile, "r", encoding="utf8").read()

    blocks = parse_interval_blocks(text)
    print(f"Found {len(blocks)} Intervallmuster blocks.")

    matches = detect_rotations(blocks)
    print(f"Detected {len(matches)} rotational matches.")

    write_ttl(matches)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python match_rotations.py input.ttl")
        sys.exit(1)
    main(sys.argv[1])
