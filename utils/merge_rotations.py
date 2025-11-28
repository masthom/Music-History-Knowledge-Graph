import re

# ---------------------------------------------------------
# Hilfsfunktionen zur Rotationserzeugung
# ---------------------------------------------------------

def calculate_closure_interval(interval_pattern):
    """Berechnet das Abschlussintervall eines Intervallmusters."""
    intervals = list(map(int, interval_pattern.split('_')))
    pc = 0
    for iv in intervals:
        pc = (pc + iv) % 12
    closure = (-pc) % 12
    intervals.append(closure)
    return "_".join(map(str, intervals))


def generate_rotations(pattern_str):
    """Erzeugt alle Rotationen eines '_' getrennten Strings."""
    parts = pattern_str.split('_')
    return ["_".join(parts[i:] + parts[:i]) for i in range(len(parts))]


def find_canonical_group_name(patterns):
    """Wählt das numerisch kleinste Pattern als kanonischen Namen."""
    return min(patterns, key=lambda x: [int(p) for p in x.split('_')])


def numeric_sort_key(prefix, full_name):
    """Extrahiert Zahlen aus z.B. 'mhg:rotationGroup_3_10_2'."""
    tail = full_name[len(prefix):]
    return [int(x) for x in tail.split('_') if x.isdigit()]


# ---------------------------------------------------------
# Hauptfunktion zur Integration
# ---------------------------------------------------------

def integrate_rotations(input_path, output_path):

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # -----------------------------------------------------
    # 1) Erkennen der echten IntervalPattern-Zweizeiler
    # -----------------------------------------------------

    ip_line_re = re.compile(
        r"^mhg:ip_(?P<pattern>[0-9_]+)\s+a\s+mhg:intervalPattern\s*;\s*$"
    )

    hasrow_re = re.compile(
        r"^mhg:hasRowClass\s+(?P<rc>mhg:rc_[0-9_]+)\s*\.\s*$"
    )

    ip_records = {}  # pattern → {ip_idx, rc_idx, rc_name}
    i = 0
    n = len(lines)

    while i < n:
        m = ip_line_re.match(lines[i])
        if m:
            pattern = m.group("pattern")
            if i + 1 < n:
                m2 = hasrow_re.match(lines[i + 1])
                if m2:
                    rc_name = m2.group("rc")
                    ip_records[pattern] = {
                        "ip_idx": i,
                        "rc_idx": i + 1,
                        "rc_name": rc_name,
                    }
                    i += 2
                    continue
        i += 1

    print("Gefundene IntervalPattern-Einträge:", len(ip_records))

    # -----------------------------------------------------
    # 2) Gruppenbildung: geschlossene Formen + Rotationen
    # -----------------------------------------------------

    closed_groups = {}
    for pattern in ip_records.keys():
        n_len = len(pattern.split('_'))
        closed = calculate_closure_interval(pattern)
        rotations_closed = generate_rotations(closed)
        canonical_closed = find_canonical_group_name(rotations_closed)
        if canonical_closed not in closed_groups:
            closed_groups[canonical_closed] = {
                "length": n_len,
                "members": set()
            }
        closed_groups[canonical_closed]["members"].add(pattern)

    # -----------------------------------------------------
    # 3) RotationGroups erzeugen (verkürzt um Abschlussintervall)
    # -----------------------------------------------------

    rotation_groups = {}  # canonical → {all_rotations, found_patterns}
    for closed_can, info in closed_groups.items():
        L = info["length"]
        all_rot = []
        for rot in generate_rotations(closed_can):
            parts = rot.split('_')
            all_rot.append("_".join(parts[:L]))
        canonical = all_rot[0]
        rotation_groups[canonical] = {
            "all_rotations": all_rot,
            "found_patterns": info["members"]
        }

    print("Generierte Rotationsgruppen:", len(rotation_groups))

    # -----------------------------------------------------
    # 4) Mapping pattern → RotationGroup + rotationIndex
    # -----------------------------------------------------

    pattern_assignment = {}
    for canonical, data in rotation_groups.items():
        members = data["all_rotations"]
        for idx, mpat in enumerate(members):
            if mpat in data["found_patterns"]:
                pattern_assignment[mpat] = (canonical, idx)

    # -----------------------------------------------------
    # 5) Die Original-IP-Tripel ersetzen / erweitern
    #     gemäß Variante B (alles eingerückt)
    # -----------------------------------------------------

    new_lines = list(lines)
    replacements = []

    for pattern, rec in ip_records.items():
        rc_idx = rec["rc_idx"]
        rc_line = lines[rc_idx].rstrip()

        if pattern not in pattern_assignment:
            continue

        canonical, rot_index = pattern_assignment[pattern]

        # erste Zeile (ip_) bleibt wie sie ist
        ip_line = lines[rec["ip_idx"]].rstrip()

        # neue, erweiterte Struktur
        indent = "    "  # vier Leerzeichen – Variante B

        new_block = (
            f"{ip_line}\n"
            f"{indent}mhg:hasRowClass {rec['rc_name']} ;\n"
            f"{indent}mhg:hasRotationGroup mhg:rotationGroup_{canonical} ;\n"
            f"{indent}mhg:rotationIndex {rot_index} .\n"
        )

        replacements.append((rec["ip_idx"], rec["rc_idx"], new_block))

    # nach hinten sortieren, damit indices stabil bleiben
    replacements.sort(reverse=True)

    for ip_idx, rc_idx, text in replacements:
        new_lines[ip_idx:rc_idx + 1] = [text]

    # -----------------------------------------------------
    # 6) RotationGroups sortiert ans Ende anhängen
    # -----------------------------------------------------

    rg_names = list(rotation_groups.keys())
    full_rg = [f"mhg:rotationGroup_{name}" for name in rg_names]
    sorted_rg = sorted(full_rg,
                       key=lambda x: numeric_sort_key("mhg:rotationGroup_", x))

    new_lines.append("\n# --- autogenerated rotationGroups ---\n")

    for full in sorted_rg:
        canonical = full.split("mhg:rotationGroup_")[1]
        group_data = rotation_groups[canonical]
        members = group_data["all_rotations"]
        found = group_data["found_patterns"]

        block = []
        block.append(f"{full} a mhg:rotationGroup ;\n")
        block.append("    mhg:hasRotationGroupElement ")

        elems = []
        for i, mem in enumerate(members):
            base = f"mhg:ip_{mem}"
            if mem not in found:
                if i < len(members) - 1:
                    elems.append(f"{base} ,  ##not yet detected")
                else:
                    elems.append(f"{base} .  ##not yet detected")
            else:
                if i < len(members) - 1:
                    elems.append(f"{base} ,")
                else:
                    elems.append(f"{base} .")

        block.append((" \n                 ".join(elems)) + "\n\n")
        new_lines.append("".join(block))

    # -----------------------------------------------------
    # 7) Ausgabe schreiben
    # -----------------------------------------------------

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("Fertig. Neue Datei erzeugt:", output_path)


# ---------------------------------------------------------
# Aufruf
# ---------------------------------------------------------

if __name__ == "__main__":
    input_path = "MusicHistoryGraph_TwelveToneMusic_Reordered.ttl"
    output_path = "MusicHistoryGraph_TwelveToneMusic_WithRotations.ttl"

    integrate_rotations(input_path, output_path)
