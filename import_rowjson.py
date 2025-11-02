#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import und Umwandlung von rows.json -> output.json
Korrekte Intervallberechnung: für jede Form (P0,I,R,RI) werden
die Intervalle direkt aus der jeweiligen Pitch-Sequenz berechnet.
Zusätzlich: OriginalP und dessen Intervalle.
"""

import json
import argparse
from typing import List, Tuple, Dict

def intervals(row: List[int]) -> List[int]:
    """(x_{i+1}-x_i) mod 12 für i=0..n-2"""
    return [ (row[i+1] - row[i]) % 12 for i in range(len(row)-1) ]

def inversion_by_first(row: List[int]) -> List[int]:
    """Inversion um den ersten Ton p0: i_k = (2*p0 - p_k) mod 12"""
    p0 = row[0]
    return [ (2*p0 - p) % 12 for p in row ]

def retrograde(row: List[int]) -> List[int]:
    return list(reversed(row))

def format_mhg(seq: List[int]) -> str:
    return "mhg:" + "_".join(str(x) for x in seq)

def parse_mhg_tuple(mhg: str) -> Tuple[int, ...]:
    assert mhg.startswith("mhg:")
    parts = mhg[4:].split("_") if len(mhg) > 4 else []
    return tuple(int(p) for p in parts)

def transpose_to_first(row: List[int], new_first: int) -> List[int]:
    shift = (new_first - row[0]) % 12
    return [(p + shift) % 12 for p in row]

def generate_48_from_base(base_row: List[int]) -> List[str]:
    inv = inversion_by_first(base_row)
    ret = retrograde(base_row)
    retinv = retrograde(inv)
    out = []
    for form in (base_row, inv, ret, retinv):
        for t in range(12):
            trans = [(p + t) % 12 for p in form]
            out.append(format_mhg(trans))
    return out

def compute_forms_pitch_and_intervals(row: List[int]) -> Dict[str, Dict[str, List[int]]]:
    """
    Liefert für P0/I/R/RI jeweils die Pitch-Sequenz und das Intervallmuster.
    Rückgabeformat:
      { "P0": {"pitches": [...], "intervals": [...]}, ... }
    """
    p0 = row
    i = inversion_by_first(row)
    r = retrograde(row)
    ri = retrograde(i)
    res = {}
    for label, seq in (("P0", p0), ("I", i), ("R", r), ("RI", ri)):
        res[label] = {
            "pitches": seq,
            "intervals": intervals(seq)
        }
    return res

def main(infile: str, outfile: str):
    with open(infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = {}

    for key, info in data.items():
        if not isinstance(info, dict) or "P0" not in info:
            print(f"⚠️ Übersprungen (kein P0): {key}")
            continue

        row = info["P0"]
        if not isinstance(row, list) or len(row) < 2:
            print(f"⚠️ Ungültige Reihe bei {key} — übersprungen.")
            continue

        # Berechne Pitches und Intervalle für alle 4 Formen
        forms = compute_forms_pitch_and_intervals(row)

        # mhg-Strings für Intervalle
        mhg_map = { label: format_mhg(forms[label]["intervals"]) for label in forms }

        # Sortierung: zahlweise lexikographisch anhand der Interval-Tupel
        sortable = []
        for label in ("P0","I","R","RI"):
            tup = tuple(forms[label]["intervals"])
            sortable.append( (tup, mhg_map[label], label) )
        sortable_sorted = sorted(sortable, key=lambda x: x[0])
        sorted_mhg_list = [x[1] for x in sortable_sorted]
        # kleinste Form (Label) aus der sortierten Liste
        smallest_label = sortable_sorted[0][2]

        # OriginalP: transponiere P0 so, dass erster Ton = info["Original"] (falls angegeben)
        if "Original" in info and info["Original"] is not None:
            try:
                orig_val = int(info["Original"])
                original_pitches = transpose_to_first(row, orig_val)
            except Exception:
                print(f"⚠️ Ungültiger Original-Wert bei {key}: {info['Original']}")
                original_pitches = row[:]  # fallback
        else:
            original_pitches = row[:]

        original_intervals = intervals(original_pitches)

        # Bestimme die Basisreihe (P, I, R oder RI) für die Erzeugung der 48 Formen
        if smallest_label == "P0":
            base_row = forms["P0"]["pitches"]
        elif smallest_label == "I":
            base_row = forms["I"]["pitches"]
        elif smallest_label == "R":
            base_row = forms["R"]["pitches"]
        elif smallest_label == "RI":
            base_row = forms["RI"]["pitches"]
        else:
            base_row = row[:]  # fallback

        all_48 = generate_48_from_base(base_row)

        # Debug-Check: falls der key genau deinem Beispiel entspricht, prüfe das P0-Intervall
        # (ändere ggf. den Key-String auf deinen tatsächlichen Key)
        example_key = "Apostel,_Hans_Erich_-_Fischerhaus-Serenade,_Op.45"
        if key == example_key:
            expected = [4,4,7,8,8,6,8,8,9,8,8]
            actual = forms["P0"]["intervals"]
            if actual != expected:
                print("‼️ Achtung: P0-Intervall stimmt nicht für", key)
                print("  Erwartet:", expected)
                print("  Gefunden:", actual)
            else:
                print("✔ P0-Intervall korrekt für", key)

        # Schreibe Output-Eintrag
        output[key] = {
            "Composer": info.get("Composer"),
            "Work": info.get("Work"),
            "Original": info.get("Original"),
            "Year": info.get("Year"),
            "Source": info.get("Source"),
            "SortedIntervalPatterns": sorted_mhg_list,
            "OriginalP": format_mhg(original_pitches),
            "OriginalPIntervals": format_mhg(original_intervals),
            "All48Forms": all_48
        }

    # Schreibe JSON
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("✅ Fertig. Output geschrieben in", outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="rows.json")
    parser.add_argument("--out", dest="outfile", default="output.json")
    args = parser.parse_args()
    main(args.infile, args.outfile)
