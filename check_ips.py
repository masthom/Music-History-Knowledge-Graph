import re

ttl_file = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"

# Regex für IP-Elemente
ip_pattern = re.compile(r"mhg:ip_[0-9_]+")

# Speicherung
ip_marked = set()
ip_as_intervalpattern = set()

with open(ttl_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# ------------------------------------------------------
# 1. Alle IPs sammeln, die im Typ (2) als intervalPattern vorkommen
# ------------------------------------------------------
for line in lines:
    if "a mhg:intervalPattern" in line:
        for ip in ip_pattern.findall(line):
            ip_as_intervalpattern.add(ip)

# ------------------------------------------------------
# 2. Alle IPs sammeln, die in (1) als "not yet detected" markiert sind
# ------------------------------------------------------
inside_rotation_group = False
current_block = []

for line in lines:

    if line.startswith("mhg:rotationGroup_"):
        inside_rotation_group = True

    if inside_rotation_group:
        current_block.append(line)

        # Blockende
        if line.strip().endswith("."):
            # Suche nach allen IPs im Block und prüfe je nach Kommentar
            for l in current_block:

                # Alle IPs in der Zeile extrahieren
                ips_in_line = ip_pattern.findall(l)

                if not ips_in_line:
                    continue

                # Wenn die Zeile "##not yet detected" enthält,
                # dann gehören *alle IPs in dieser Zeile* dazu.
                if "##not yet detected" in l:
                    for ip in ips_in_line:
                        ip_marked.add(ip)

            current_block = []
            inside_rotation_group = False

# ------------------------------------------------------
# 3. Schnittmenge: markiert, aber existieren in (2)
# ------------------------------------------------------
detected = ip_marked.intersection(ip_as_intervalpattern)

# ------------------------------------------------------
# Ausgabe
# ------------------------------------------------------
print("IPs, die als '##not yet detected' markiert sind, aber tatsächlich als intervalPattern vorkommen:\n")

if detected:
    for ip in sorted(detected):
        print(ip)
else:
    print("Keine solchen IP-Elemente gefunden.")
