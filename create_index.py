import re

def update_ttl_file(input_ttl_path, output_ttl_path):
    # Lese die Eingabedatei
    with open(input_ttl_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Ersetze rowClass-Deklarationen
    content = re.sub(
        r'mhg:([0-9_]+)\s+a\s+mhg:rowClass',
        r'mhg:rc_\1 a mhg:rowClass',
        content
    )
    
    # 2. Ersetze hasRowClass-Referenzen
    content = re.sub(
        r'mhg:hasRowClass mhg:([0-9_]+)',
        r'mhg:hasRowClass mhg:rc_\1',
        content
    )
    
    # 3. Ersetze rowForm-Deklarationen
    content = re.sub(
        r'mhg:([0-9_]+)\s+a\s+mhg:rowForm',
        r'mhg:rf_\1 a mhg:rowForm',
        content
    )
    
    # 4. Ersetze hasRowForm-Referenzen (einschließlich Listen)
    # Regex für hasRowForm-Listen, die über mehrere Zeilen gehen können
    pattern = r'(mhg:hasRowForm\s+)([^;]+)(;)'
    
    def replace_hasrowform(match):
        prefix = match.group(1)
        forms_list = match.group(2)
        suffix = match.group(3)
        
        # Ersetze jede Referenz in der Liste
        new_forms_list = re.sub(
            r'mhg:([0-9_]+)',
            r'mhg:rf_\1',
            forms_list
        )
        
        return prefix + new_forms_list + suffix
    
    content = re.sub(pattern, replace_hasrowform, content, flags=re.DOTALL)
    
    # Schreibe die Ausgabedatei
    with open(output_ttl_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"TTL-Datei wurde aktualisiert: {output_ttl_path}")

if __name__ == "__main__":
    input_ttl = "transformations5.ttl"  # Ihre Eingabedatei
    output_ttl = "transformations5_index.ttl"  # Ihre Ausgabedatei
    update_ttl_file(input_ttl, output_ttl)