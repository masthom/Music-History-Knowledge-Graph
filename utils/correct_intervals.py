import re

def parse_interval_string(s):
    """Parse an interval string into a list of integers."""
    return [int(x) for x in s.split('_')]

def format_interval_string(intervals):
    """Format a list of integers back into the string representation."""
    return '_'.join(str(x) for x in intervals)

def calculate_forms(p_intervals):
    """Calculate all derivative forms from the prime form."""
    # Inversion: each interval complements to 12
    i_intervals = [12 - x for x in p_intervals]
    
    # Retrograde: reverse of prime
    r_intervals = p_intervals[::-1]
    
    # Retrograde Inversion: reverse of inversion
    ri_intervals = i_intervals[::-1]
    
    return {
        'P': p_intervals,
        'I': i_intervals,
        'R': r_intervals,
        'RI': ri_intervals
    }

def correct_interval_block(block_lines):
    """Correct a single interval pattern block."""
    # Extract the interval strings using regex
    patterns = []
    labels = []
    
    for line in block_lines[1:5]:  # Skip the header line
        match = re.search(r'##\s*(\w+):\s*([\d_]+)$', line.strip())
        if match:
            labels.append(match.group(1))
            patterns.append(match.group(2))
    
    if len(patterns) != 4:
        return block_lines  # Return unchanged if pattern is invalid
    
    # Find the P line
    p_index = None
    p_str = None
    for i, label in enumerate(labels):
        if label == 'P':
            p_index = i
            p_str = patterns[i]
            break
    
    if p_index is None:
        return block_lines  # Return unchanged if no P found
    
    # Parse intervals from P
    p_intervals = parse_interval_string(p_str)
    
    # Calculate correct forms
    correct_forms = calculate_forms(p_intervals)
    
    # Parse the provided forms (excluding P)
    provided_forms = {}
    for i, (label, pattern) in enumerate(zip(labels, patterns)):
        if i != p_index:  # Skip P
            provided_forms[label] = parse_interval_string(pattern)
    
    # Find correct labels for each provided form
    label_mapping = {}
    used_labels = set(['P'])  # P is already used
    
    for provided_label, provided_intervals in provided_forms.items():
        for correct_label, correct_intervals in correct_forms.items():
            if (correct_label not in used_labels and 
                provided_intervals == correct_intervals):
                label_mapping[provided_label] = correct_label
                used_labels.add(correct_label)
                break
    
    # Reconstruct the block with P always first
    corrected_block = [block_lines[0]]  # Keep the header
    
    # Always add P first
    corrected_block.append(f"## P: {p_str}")
    
    # Add the other forms in the order they appear in the original block, but skip P
    for i, (label, pattern) in enumerate(zip(labels, patterns)):
        if i != p_index:  # Skip P (we already added it)
            if label in label_mapping:
                corrected_block.append(f"## {label_mapping[label]}: {pattern}")
            else:
                corrected_block.append(f"## {label}: {pattern}")
    
    # Add any remaining lines from the original block
    if len(block_lines) > 5:
        corrected_block.extend(block_lines[5:])
    
    return corrected_block

def process_ttl_file(input_file, output_file):
    """Process entire TTL file and correct all interval pattern blocks."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into lines
        lines = content.split('\n')
        
        # Find all interval pattern blocks
        corrected_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line starts an interval pattern block
            if line.startswith('## Intervallmuster:'):
                # Collect the block (next 4 lines should be P, I, R, RI)
                block_lines = [lines[i]]
                
                # Add the next 4 lines (or as many as available)
                for j in range(1, 5):
                    if i + j < len(lines) and lines[i + j].strip().startswith('##'):
                        block_lines.append(lines[i + j])
                    else:
                        # If we don't have 4 pattern lines, keep the block as is
                        break
                
                # Correct the block if we have all 4 pattern lines
                if len(block_lines) == 5:
                    corrected_block = correct_interval_block(block_lines)
                    corrected_lines.extend(corrected_block)
                    i += 4  # Skip the 4 pattern lines we just processed
                else:
                    corrected_lines.extend(block_lines)
                    i += len(block_lines) - 1
            else:
                corrected_lines.append(lines[i])
            
            i += 1
        
        # Write corrected content to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(corrected_lines))
        
        print(f"Successfully processed {input_file} -> {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Error processing file: {e}")

def main():
    """Main function to handle file processing."""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python correct_intervals.py input.ttl output.ttl")
        print("Or provide filenames when prompted.")
        
        input_file = input("Enter input TTL filename: ").strip()
        output_file = input("Enter output TTL filename: ").strip()
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    
    process_ttl_file(input_file, output_file)

if __name__ == "__main__":
    main()