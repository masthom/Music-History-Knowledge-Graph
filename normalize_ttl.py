# normalize_ttl_uris_from_original.py
import re
import unicodedata
import csv
from pathlib import Path

# ======== CONFIG ========
INPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_NEW.ttl"
OUTPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_NORMALIZED_SAFE.ttl"
CSV_LOG = "Normalization_Mapping.csv"
# ========================

# Phase 1: Akzent-/Umlaut-Entfernung + Zeichensatzvereinheitlichung
REPLACEMENTS = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "ß": "ss",
    "à": "a", "á": "a", "â": "a", "ã": "a", "å": "a",
    "è": "e", "é": "e", "ê": "e", "ë": "e",
    "ì": "i", "í": "i", "î": "i", "ï": "i",
    "ò": "o", "ó": "o", "ô": "o", "õ": "o",
    "ù": "u", "ú": "u", "û": "u",
    "ç": "c", "ñ": "n",
    "œ": "oe", "æ": "ae",
    "’": "_", "‘": "_", "'": "_", "`": "_", "´": "_",
    " ": "_", "-": "_", ",": "_", ".": "_",
    "(": "_", ")": "_", "[": "_", "]": "_",
}

# Phase 2: typische "kaputte" Schreibungen mit Unterstrich
BROKEN_PATTERNS = {
    "Po_me": "Poeme",   # aus "Poème"
    "Zwoelf": "Zwoelf", # Zwölf
    "Traeumerei": "Traeumerei",
    "Fuer": "Fuer",
    "L_Amour": "L_Amour",
    "_oe": "oe", "_ue": "ue", "_ae": "ae"
}


def remove_combining(s: str) -> str:
    """Entfernt Unicode-Kombinationszeichen (Akzente, Tilden etc.)"""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def normalize_localpart(local: str) -> (str, bool):
    """Normalisiert den LocalPart hinter 'mhg:'."""
    orig = local
    s = remove_combining(local)
    phase2 = False

    for bad, fixed in BROKEN_PATTERNS.items():
        if bad in s:
            s = s.replace(bad, fixed)
            phase2 = True

    for k, v in REPLACEMENTS.items():
        if k in s:
            s = s.replace(k, v)

    # Erlaubte Zeichen
    s = re.sub(r"[^A-Za-z0-9_\-\.]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")

    return s or orig, phase2


def main():
    p_in = Path(INPUT_FILE)
    p_out = Path(OUTPUT_FILE)
    csv_path = Path(CSV_LOG)

    text = p_in.read_text(encoding="utf-8")

    # Nur Tokens mit Präfix 'mhg:' finden
    pattern = re.compile(r'\bmhg:([A-Za-z0-9_\-\.éèàùüÄÖÜßçñ’\'´`]+)')
    seen = {}
    phase2_flags = {}

    def repl(match):
        local = match.group(1)
        if local in seen:
            normalized = seen[local]
            return f"mhg:{normalized}"
        new_local, phase2 = normalize_localpart(local)
        seen[local] = new_local
        phase2_flags[local] = phase2
        return f"mhg:{new_local}"

    new_text = pattern.sub(repl, text)

    # Mapping als CSV-Log
    with csv_path.open("w", encoding="utf-8", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["old_local", "new_local", "phase2_flag"])
        for old, new in sorted(seen.items()):
            writer.writerow([old, new, int(phase2_flags.get(old, False))])

    p_out.write_text(new_text, encoding="utf-8")

    print(f"✅ Normalisierung abgeschlossen.")
    print(f"   Eingabe:  {p_in}")
    print(f"   Ausgabe:  {p_out}")
    print(f"   Log:      {csv_path}")
    print(f"   {len(seen)} URIs überprüft, {sum(1 for k,v in seen.items() if k!=v)} geändert.")
    print(f"   {sum(phase2_flags.values())} davon mit Phase-2-Korrektur.")


if __name__ == "__main__":
    main()
