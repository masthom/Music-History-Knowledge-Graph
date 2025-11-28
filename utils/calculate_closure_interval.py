def calculate_closure_interval(interval_pattern):
    # Intervalle in eine Liste von Integers umwandeln
    intervals = list(map(int, interval_pattern.split('_')))
    
    # Kumulative Summe modulo 12 berechnen (beginnend bei 0)
    current_pc = 0
    for interval in intervals:
        current_pc = (current_pc + interval) % 12
    
    # Intervall zwischen letztem und erstem Ton berechnen
    closure_interval = (0 - current_pc) % 12
    
    # Neues Intervall an die ursprüngliche Liste anhängen
    intervals.append(closure_interval)
    
    # Zurück in String-Format mit Unterstrichen konvertieren
    return '_'.join(map(str, intervals))

# Beispiel ausführen
if __name__ == "__main__":
    input_pattern = "1_2_3"
    result = calculate_closure_interval(input_pattern)
    print(f"Eingabe: {input_pattern}")
    print(f"Ergebnis: {result}")