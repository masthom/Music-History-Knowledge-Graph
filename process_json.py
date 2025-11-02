import json

def process_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    turtle_output = []
    
    # Add prefixes
    turtle_output.append("@prefix mhg: <http://example.org/mhg/> .")
    turtle_output.append("@prefix frbr: <http://purl.org/vocab/frbr/core#> .")
    turtle_output.append("")

    for work_key, work_data in data.items():
        if not isinstance(work_data, dict):
            continue
            
        # Clean work name to be used as identifier
        work_id = work_key.replace(",_", "_").replace(" ", "_").replace("'", "").replace(".", "")
        
        # Basic work declaration
        turtle_output.append(f"mhg:{work_id} a mhg:composition, frbr:work ;")
        
        # Add composer if present
        if "Composer" in work_data:
            composer = work_data["Composer"].replace(",", "").replace(" ", "_")
            turtle_output.append(f"    frbr:creator mhg:{composer} ;")
        
        # Add creation date if present
        if "Year" in work_data and work_data["Year"]:
            turtle_output.append(f"    frbr:hasCreationDate \"{work_data['Year']}\" .")
        else:
            turtle_output.append("    .")

        # Process first interval pattern if present
        if "SortedIntervalPatterns" in work_data and work_data["SortedIntervalPatterns"]:
            patterns = work_data["SortedIntervalPatterns"]
            if patterns and len(patterns) > 0:
                first_pattern = patterns[0]
                if first_pattern.startswith("mhg:"):
                    pattern_id = first_pattern[4:]  # Remove "mhg:" prefix
                    turtle_output.append(f"\nmhg:{pattern_id} a mhg:RowClass ;")
                    turtle_output.append(f"    mhg:actualizedIn mhg:{work_id} .")
        
        turtle_output.append("")  # Add blank line between works

    # Write output to file
    with open('compositions.ttl', 'w', encoding='utf-8') as f:
        f.write('\n'.join(turtle_output))

# Run the script
process_json('output.json')