import re
import sys
from datetime import datetime

# ---------------------------------------------------------
# Utility: Parse "mhg:1_2_3_..." → [1,2,3,...]
# ---------------------------------------------------------
def parse_qname(q):
    return list(map(int, q.split(":")[1].split("_")))

def fmt(seq):
    return "_".join(str(x) for x in seq)

# ---------------------------------------------------------
# Re-generate P, I, R, RI from an interval pattern
# ---------------------------------------------------------
def row_from_intervals(intervals, start=0, mod=12):
    row = [start]
    for iv in intervals:
        row.append((row[-1] + iv) % mod)
    return row

def invert_row(row):
    return [(-p) % 12 for p in row]

def transpose_row(row, n):
    return [(p + n) % 12 for p in row]

def retrograde(row):
    return list(reversed(row))

def generate_all_forms(intervals):
    """Returns a set of all RowForms derivable from the interval pattern."""
    all_forms = set()

    # P-Forms
    P0 = row_from_intervals(intervals, 0)
    for t in range(12):
        all_forms.add(tuple(transpose_row(P0, t)))

    # I-Forms
    I0 = invert_row(P0)
    for t in range(12):
        all_forms.add(tuple(transpose_row(I0, t)))

    # R-Forms
    for t in range(12):
        all_forms.add(tuple(retrograde(transpose_row(P0, t))))

    # RI-Forms
    for t in range(12):
        all_forms.add(tuple(retrograde(transpose_row(I0, t))))

    return all_forms

# ---------------------------------------------------------
# Parse TTL content
# ---------------------------------------------------------
def extract_rowclasses_and_rowforms(ttl_text):
    rowclasses = {}  # rowClassQName → set(rowFormQNames)

    # Regex to match:  mhg:<intervals> a mhg:rowClass ;
    rowclass_pattern = re.compile(r"(mhg:[0-9_]+)\s+a\s+mhg:rowClass\s*;")

    # Regex for its rowForms inside "mhg:hasRowForm ..."
    rowform_pattern = re.compile(r"mhg:([0-9_]+)")

    lines = ttl_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Found a rowClass block
        m = rowclass_pattern.search(line)
        if m:
            rc_qname = m.group(1)
            rowclasses[rc_qname] = set()

            # Read following lines until we hit a "."
            j = i + 1
            while j < len(lines):
                if "." in lines[j]:
                    break
                for rf in rowform_pattern.findall(lines[j]):
                    if "_" in rf:  # avoid accidental matches
                        rowclasses[rc_qname].add("mhg:" + rf)
                j += 1

            i = j
        i += 1

    return rowclasses

# ---------------------------------------------------------
# Validate + TXT output
# ---------------------------------------------------------
def validate_ttl(ttl_path, output_txt="validation_log.txt"):
    with open(ttl_path, "r", encoding="utf-8") as f:
        ttl_text = f.read()

    rowclasses = extract_rowclasses_and_rowforms(ttl_text)

    log_lines = []
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines.append(f"Validation Log – {time_stamp}")
    log_lines.append("=" * 60)

    for rc_qname, rowforms in rowclasses.items():
        log_lines.append(f"\nChecking rowClass {rc_qname} ...")

        intervals = parse_qname(rc_qname)
        expected_forms = generate_all_forms(intervals)

        # Convert rowforms from QNames to tuples
        rowforms_tuples = {tuple(parse_qname(rf)) for rf in rowforms}

        # Compare
        missing = rowforms_tuples - expected_forms
        extra = expected_forms - rowforms_tuples  # Not errors, just informative

        if not missing:
            msg = "  ✔ All rowForms consistent with interval pattern."
            print(msg)
            log_lines.append(msg)
        else:
            msg = "  ❌ Incorrect or inconsistent rowForms:"
            print(msg)
            log_lines.append(msg)
            for bad in missing:
                line = "     → " + fmt(list(bad))
                print(line)
                log_lines.append(line)

        msg_count_ttl = f"  Total rowForms in TTL: {len(rowforms_tuples)}"
        msg_count_deriv = f"  Total rowForms derivable: {len(expected_forms)}"

        print(msg_count_ttl)
        print(msg_count_deriv)

        log_lines.append(msg_count_ttl)
        log_lines.append(msg_count_deriv)

    # Write TXT log
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\nLog written to: {output_txt}")


# ---------------------------------------------------------
# Run example
# ---------------------------------------------------------
if __name__ == "__main__":
    validate_ttl("MusicHistoryGraph_TwelveToneMusic_Complete.ttl")
