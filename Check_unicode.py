with open("MusicHistoryGraph_TwelveToneMusic_TEST.ttl", "rb") as f:
    content = f.read()

# Suche nach "verdächtigen" Unicode-Bytes
suspicious = [b"\xef\xbb\xbf", b"\x00", b"\xa0", b"\xe2\x80\x8b"]  # BOM, NULL, nbsp, zero-width space
for seq in suspicious:
    if seq in content:
        print(f"⚠️ Gefunden: {seq} bei Position {content.find(seq)}")

