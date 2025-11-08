import chardet

def check_ttl_encoding(file_path):
    # 1️⃣ Datei binär lesen
    with open(file_path, "rb") as f:
        raw = f.read()

    # 2️⃣ Encoding automatisch erkennen
    detection = chardet.detect(raw)
    encoding = detection.get("encoding")
    confidence = detection.get("confidence", 0)

    print(f"🔎 Erkanntes Encoding: {encoding} (Sicherheit: {confidence:.2f})")

    # 3️⃣ BOM-Prüfung
    if raw.startswith(b"\xef\xbb\xbf"):
        print("⚠️ UTF-8 BOM gefunden! Entferne es (UTF-8 **ohne BOM** speichern).")
    elif raw.startswith(b"\xff\xfe"):
        print("⚠️ UTF-16 Little Endian erkannt – bitte in UTF-8 konvertieren.")
    elif raw.startswith(b"\xfe\xff"):
        print("⚠️ UTF-16 Big Endian erkannt – bitte in UTF-8 konvertieren.")
    else:
        print("✅ Kein BOM gefunden.")

    # 4️⃣ Suche nach Steuerzeichen oder Nullbytes
    bad_chars = []
    for i, b in enumerate(raw):
        if b in (0x00, 0x1A):  # NULL oder CTRL-Z
            bad_chars.append((i, b))
    if bad_chars:
        print("⚠️ Steuerzeichen gefunden:")
        for i, b in bad_chars[:10]:
            print(f"   - Position {i}: Byte {b:#04x}")
    else:
        print("✅ Keine Steuerzeichen gefunden.")

    # 5️⃣ Optional: Zeilenendungen prüfen
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf > 0:
        print(f"⚠️ {crlf} Zeilen mit Windows-CRLF gefunden.")
    else:
        print("✅ Nur UNIX-Zeilenenden (LF).")

    print("\nEmpfohlene Aktion:")
    print("➡️ Öffne Datei in VS Code oder Notepad++ und speichere als:")
    print("   UTF-8 (ohne BOM) + Zeilenenden LF\n")


# Beispielaufruf:
if __name__ == "__main__":
    check_ttl_encoding("Composers_Works_Rows_SerialAnalyzer.ttl")
