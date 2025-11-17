import re
from datetime import datetime

# --- Konfiguration ---
TTL_FILE = "MusicHistoryGraph_TwelveToneMusic_Complete.ttl"

# Regex zum Finden von xsd:date-Literalen
DATE_PATTERN = re.compile(r'"([^"]+)"\^\^xsd:date')

def is_valid_xsd_date(date_str: str) -> bool:
    """
    Prüft, ob ein Datum im Format YYYY-MM-DD gültig ist.
    """
    try:
        # Muss GENAU das Format haben
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def main():
    print("🔍 Checking dates in:", TTL_FILE)
    print("=" * 50)

    with open(TTL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    errors = []
    for i, line in enumerate(lines, start=1):
        matches = DATE_PATTERN.findall(line)
        for date_str in matches:
            if not is_valid_xsd_date(date_str):
                errors.append((i, date_str, line.strip()))

    if errors:
        print("❌ INVALID DATES FOUND:")
        print("=" * 50)
        for lineno, date_str, context in errors:
            print(f"Line {lineno}: invalid date → {date_str}")
            print(f"    {context}")
            print("-" * 50)
    else:
        print("✅ No invalid xsd:date literals found.")

if __name__ == "__main__":
    main()
