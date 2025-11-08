def normalize_ttl_line_endings(file_path, output_path=None):
    output_path = output_path or file_path
    with open(file_path, "rb") as f:
        data = f.read()

    # CRLF -> LF
    data = data.replace(b"\r\n", b"\n")

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"✅ Zeilenenden in '{output_path}' vereinheitlicht (LF, UTF-8 ohne BOM).")

# Beispielaufruf:
if __name__ == "__main__":
    normalize_ttl_line_endings(
        "MusicHistoryGraph_TwelveToneMusic_TEST.ttl"
    )
