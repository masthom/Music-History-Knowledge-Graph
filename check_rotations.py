import re

def parse_rowclass(line):
    """Extrahiert eine mhg:1_2_3_... Sequenz."""
    m = re.search(r"mhg:([\d_]+)", line)
    return m.group(1) if m else None

def parse_ttl_rowclasses(path):
    rowclasses = []
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            if "a mhg:rowClass" in line:
                rc = parse_rowclass(line)
                if rc:
                    nums = list(map(int, rc.split("_")))
                    rowclasses.append((rc, nums))
    return rowclasses

def diff_signature(nums):
    """Erzeugt die Rotations-invariante Intervall-Differenzfolge."""
    return [(nums[(i+1) % len(nums)] - nums[i]) % 12 for i in range(len(nums))]

def rotation_shift(a, b):
    """Bestimmt, ob b eine Rotation von a ist und liefert den Shift."""
    if len(a) != len(b):
        return None
    n = len(a)
    for s in range(n):
        if all(a[(i+s) % n] == b[i] for i in range(n)):
            return s
    return None

def detect_rotations(rowclasses):
    """Ermittelt Rotationsäquivalenzen auf Basis der diff-Signaturen."""
    results = []
    diff_map = {rc: diff_signature(nums) for rc, nums in rowclasses}

    for (rcA, numsA), (rcB, numsB) in [
        (a,b) for a in rowclasses for b in rowclasses if a!=b
    ]:
        dA = diff_map[rcA]
        dB = diff_map[rcB]

        shift = rotation_shift(dA, dB)
        if shift is not None:
            results.append((rcA, rcB, shift))

    return results

def write_output(results, path):
    with open(path, "w", encoding="utf8") as f:
        for rcA, rcB, s in results:
            f.write(
                f"mhg:{rcA} mhg:isRotationOf mhg:{rcB} ;\n"
                f'    mhg:rotationShift "Rotation {s}" .\n\n'
            )

# ------------------ MAIN --------------------

INPUT = "TestRotation.ttl"
OUTPUT = "rotations.ttl"

rowclasses = parse_ttl_rowclasses(INPUT)
print(f"Loaded {len(rowclasses)} rowClasses.")

results = detect_rotations(rowclasses)
print(f"Detected {len(results)} rotational relations.")

write_output(results, OUTPUT)
print(f"Wrote: {OUTPUT}")
