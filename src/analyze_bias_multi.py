# Import libraries
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bias_detector import MultiBiasDetector
from collections import defaultdict

print("=" * 70)
print("MULTI-BIAS ANALYSIS TOOL")
print("=" * 70)

# Get bias type from command line
bias_type = sys.argv[1] if len(sys.argv) > 1 else 'combined'
print(f"\nAnalyzing: {bias_type.upper()} BIAS")
print("=" * 70)

# Determine which input file to use
if bias_type == 'gender':
    input_file = 'results/generated_outputs.txt'
elif bias_type == 'combined':
    input_file = 'results/generated_outputs_multi_bias.txt'
else:
    input_file = f'results/generated_outputs_{bias_type}.txt'

# Read the generated outputs
encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
content = None

for encoding in encodings_to_try:
    try:
        with open(input_file, 'r', encoding=encoding) as f:
            content = f.read()
        print(f"✓ File loaded successfully with {encoding} encoding ({len(content)} characters)")
        break
    except UnicodeDecodeError:
        continue
    except FileNotFoundError:
        print(f"ERROR: Could not find {input_file}")
        print(f"Please run: python src/generate_text.py {bias_type}")
        exit()

if content is None:
    print(f"ERROR: Could not read {input_file} with any encoding")
    exit()

# Parse the file
lines = content.split('\n')
results = []

print(f"✓ Found {len(lines)} lines in file")
print("✓ Parsing file...\n")

# Look for numbered entries
i = 0
while i < len(lines):
    line = lines[i].strip()
    
    if 'PROMPT:' in line.upper():
        prompt = line.split('PROMPT:', 1)[1].strip() if ':' in line else ""
        
        # Look for the OUTPUT on next line(s)
        output = ""
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if 'OUTPUT:' in next_line.upper():
                output = next_line.split('OUTPUT:', 1)[1].strip() if ':' in next_line else ""
                break
            i += 1
        
        if prompt and output:
            results.append({
                'prompt': prompt,
                'output': output
            })
            print(f"  Parsed entry {len(results)}: {prompt[:50]}...")
    
    i += 1

if len(results) == 0:
    print("\nERROR: Could not parse any results from the file!")
    exit()

print(f"\n✓ Successfully parsed {len(results)} text entries!")
print("=" * 70)

# Initialize multi-bias detector
if bias_type == 'combined':
    detector = MultiBiasDetector()  # Detect all bias types
else:
    detector = MultiBiasDetector([bias_type])  # Detect specific bias type

# Analyze each result
analyzed_results = []

for i, result in enumerate(results, 1):
    prompt = result['prompt']
    output = result['output']
    
    # Detect bias
    if bias_type == 'combined':
        bias_results = detector.detect_all(output)
    else:
        bias_results = {bias_type: detector.detect_single(output, bias_type)}
    
    # Extract subject from prompt (first few words)
    words = prompt.split()
    subject = " ".join(words[:3]) if len(words) >= 3 else prompt[:30]
    
    analyzed_results.append({
        'subject': subject,
        'prompt': prompt,
        'output': output,
        'bias_results': bias_results
    })
    
    print(f"\n[{i}/{len(results)}] {subject.upper()}")
    print(f"Prompt: {prompt}")
    print(f"Output: {output[:80]}...")
    
    for btype, bresult in bias_results.items():
        print(f"\n  {btype.upper()} BIAS:")
        print(f"    Score: {bresult['bias_score']:+.3f}")
        print(f"    Direction: {bresult['bias_direction']}")
        print(f"    Label: {bresult['bias_label']}")
        print(f"    Details: {bresult['details']}")
    
    print("-" * 70)

# Save detailed results
output_file = f'results/bias_analysis_{bias_type}_detailed.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"DETAILED {bias_type.upper()} BIAS ANALYSIS\n")
    f.write("=" * 70 + "\n\n")
    
    for i, result in enumerate(analyzed_results, 1):
        f.write(f"{i}. SUBJECT: {result['subject']}\n")
        f.write(f"   Prompt: {result['prompt']}\n")
        f.write(f"   Output: {result['output']}\n\n")
        
        for btype, bresult in result['bias_results'].items():
            f.write(f"   {btype.upper()} BIAS:\n")
            f.write(f"     Score: {bresult['bias_score']:+.3f}\n")
            f.write(f"     Direction: {bresult['bias_direction']}\n")
            f.write(f"     Label: {bresult['bias_label']}\n")
            f.write(f"     Details: {bresult['details']}\n\n")
        
        f.write("-" * 70 + "\n\n")

print(f"\n✓ Detailed analysis saved to: {output_file}")

# Calculate summary statistics
if len(analyzed_results) > 0:
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    # Aggregate statistics for each bias type
    for btype in analyzed_results[0]['bias_results'].keys():
        print(f"\n{btype.upper()} BIAS:")
        
        scores = [r['bias_results'][btype]['bias_score'] for r in analyzed_results]
        avg_score = sum(scores) / len(scores)
        
        # Count bias directions
        directions = [r['bias_results'][btype]['bias_direction'] for r in analyzed_results]
        direction_counts = defaultdict(int)
        for direction in directions:
            direction_counts[direction] += 1
        
        print(f"  Average bias score: {avg_score:+.3f}")
        print(f"  Bias distribution:")
        for direction, count in sorted(direction_counts.items()):
            print(f"    {direction}: {count} texts")
        
        # Count bias levels
        strong_bias = sum(1 for r in analyzed_results if abs(r['bias_results'][btype]['bias_score']) > 0.5)
        moderate_bias = sum(1 for r in analyzed_results if 0.3 < abs(r['bias_results'][btype]['bias_score']) <= 0.5)
        slight_bias = sum(1 for r in analyzed_results if 0.1 < abs(r['bias_results'][btype]['bias_score']) <= 0.3)
        neutral = sum(1 for r in analyzed_results if abs(r['bias_results'][btype]['bias_score']) <= 0.1)
        
        print(f"  Bias levels:")
        print(f"    Strong: {strong_bias} | Moderate: {moderate_bias} | Slight: {slight_bias} | Neutral: {neutral}")
    
    print("=" * 70)
    
    # Save summary
    summary_file = f'results/bias_summary_{bias_type}.txt'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"{bias_type.upper()} BIAS ANALYSIS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total texts analyzed: {len(analyzed_results)}\n\n")
        
        for btype in analyzed_results[0]['bias_results'].keys():
            f.write(f"{btype.upper()} BIAS:\n")
            f.write("-" * 40 + "\n")
            
            scores = [r['bias_results'][btype]['bias_score'] for r in analyzed_results]
            avg_score = sum(scores) / len(scores)
            f.write(f"Average bias score: {avg_score:+.3f}\n\n")
            
            directions = [r['bias_results'][btype]['bias_direction'] for r in analyzed_results]
            direction_counts = defaultdict(int)
            for direction in directions:
                direction_counts[direction] += 1
            
            f.write("Bias distribution:\n")
            for direction, count in sorted(direction_counts.items()):
                f.write(f"  {direction}: {count} texts\n")
            
            strong_bias = sum(1 for r in analyzed_results if abs(r['bias_results'][btype]['bias_score']) > 0.5)
            moderate_bias = sum(1 for r in analyzed_results if 0.3 < abs(r['bias_results'][btype]['bias_score']) <= 0.5)
            slight_bias = sum(1 for r in analyzed_results if 0.1 < abs(r['bias_results'][btype]['bias_score']) <= 0.3)
            neutral = sum(1 for r in analyzed_results if abs(r['bias_results'][btype]['bias_score']) <= 0.1)
            
            f.write("\nBias levels:\n")
            f.write(f"  Strong: {strong_bias}\n")
            f.write(f"  Moderate: {moderate_bias}\n")
            f.write(f"  Slight: {slight_bias}\n")
            f.write(f"  Neutral: {neutral}\n\n")
    
    print(f"\n✓ Summary saved to: {summary_file}")
    print("\n✓ Analysis complete! Check the results folder for detailed reports.")
    print("\nUsage examples:")
    print("  python src/analyze_bias_multi.py gender")
    print("  python src/analyze_bias_multi.py age")
    print("  python src/analyze_bias_multi.py combined")
