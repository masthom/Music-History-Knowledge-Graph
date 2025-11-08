with open("MusicHistoryGraph_TwelveToneMusic_TEST.ttl", "rb") as f:
    for i, line in enumerate(f, 1):
        if b'\x00' in line or b'\xef\xbb\xbf' in line:
            print("Verdächtiges Byte in Zeile", i, line)
