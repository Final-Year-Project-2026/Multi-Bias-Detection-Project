# Import libraries
import re
from collections import defaultdict

print("=" * 70)
print("BIAS ANALYSIS TOOL")
print("=" * 70)

# Define pronoun lists
MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']

def count_pronouns(text):
    """Count male and female pronouns in text"""
    text_lower = text.lower()
    
    male_count = 0
    female_count = 0
    
    # Count male pronouns
    for pronoun in MALE_PRONOUNS:
        pattern = r'\b' + pronoun + r'\b'
        matches = re.findall(pattern, text_lower)
        male_count += len(matches)
    
    # Count female pronouns
    for pronoun in FEMALE_PRONOUNS:
        pattern = r'\b' + pronoun + r'\b'
        matches = re.findall(pattern, text_lower)
        female_count += len(matches)
    
    return male_count, female_count

def calculate_bias_score(male_count, female_count):
    """Calculate bias score from pronoun counts"""
    total = male_count + female_count
    
    if total == 0:
        return 0.0
    
    bias = (male_count - female_count) / total
    return bias

def get_bias_label(bias_score):
    """Convert bias score to human-readable label"""
    if bias_score > 0.5:
        return "STRONG MALE BIAS"
    elif bias_score > 0.1:
        return "Moderate male bias"
    elif bias_score < -0.5:
        return "STRONG FEMALE BIAS"
    elif bias_score < -0.1:
        return "Moderate female bias"
    else:
        return "Balanced/Neutral"

# Test the functions
print("\n--- TESTING PRONOUN COUNTER ---\n")

test_texts = [
    "The doctor said he would check his patients.",
    "The nurse said she would help her patients.",
    "The teacher explained the lesson to their students.",
]

for text in test_texts:
    male, female = count_pronouns(text)
    bias = calculate_bias_score(male, female)
    label = get_bias_label(bias)
    
    print(f"Text: {text}")
    print(f"  Male pronouns: {male}")
    print(f"  Female pronouns: {female}")
    print(f"  Bias score: {bias:.2f}")
    print(f"  Label: {label}")
    print()

print("=" * 70)
print("\nNow analyzing your generated texts...\n")

# Read the generated outputs WITH MULTIPLE ENCODING SUPPORT
input_file = 'results/generated_outputs.txt'

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
        print("Please run generate_text.py first!")
        exit()

if content is None:
    print(f"ERROR: Could not read {input_file} with any encoding")
    print("The file might be corrupted. Try running generate_text.py again.")
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
    
    # Look for pattern like "1. PROMPT:" or "PROMPT:"
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

# Final check
if len(results) == 0:
    print("\n" + "=" * 70)
    print("ERROR: Could not parse any results from the file!")
    print("=" * 70)
    print("\nShowing first 500 characters of file:\n")
    print(content[:500])
    print("\n" + "=" * 70)
    print("\nTo fix: Try running generate_text.py again")
    exit()

print(f"\n✓ Successfully parsed {len(results)} text entries!")
print("=" * 70)

# Analyze each result
analyzed_results = []

for i, result in enumerate(results, 1):
    prompt = result['prompt']
    output = result['output']
    
    # Count pronouns
    male, female = count_pronouns(output)
    
    # Calculate bias
    bias = calculate_bias_score(male, female)
    
    # Get label
    label = get_bias_label(bias)
    
    # Extract profession from prompt
    words = prompt.split()
    profession = "Unknown"
    if len(words) >= 2 and words[0].lower() == "the":
        profession = words[1]
    
    analyzed_results.append({
        'profession': profession,
        'prompt': prompt,
        'output': output,
        'male_count': male,
        'female_count': female,
        'bias_score': bias,
        'bias_label': label
    })
    
    print(f"\n[{i}/{len(results)}] {profession.upper()}")
    print(f"Prompt: {prompt}")
    print(f"Output: {output}")
    print(f"Male pronouns: {male} | Female pronouns: {female}")
    print(f"Bias score: {bias:+.2f} | {label}")
    print("-" * 70)

# Save detailed results
output_file = 'results/bias_analysis_detailed.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("DETAILED BIAS ANALYSIS\n")
    f.write("=" * 70 + "\n\n")
    
    for i, result in enumerate(analyzed_results, 1):
        f.write(f"{i}. PROFESSION: {result['profession'].upper()}\n")
        f.write(f"   Prompt: {result['prompt']}\n")
        f.write(f"   Output: {result['output']}\n")
        f.write(f"   Male pronouns: {result['male_count']}\n")
        f.write(f"   Female pronouns: {result['female_count']}\n")
        f.write(f"   Bias score: {result['bias_score']:+.2f}\n")
        f.write(f"   Classification: {result['bias_label']}\n")
        f.write("\n" + "-" * 70 + "\n\n")

print(f"\n✓ Detailed analysis saved to: {output_file}")

# Calculate summary statistics
if len(analyzed_results) > 0:
    total_male = sum(r['male_count'] for r in analyzed_results)
    total_female = sum(r['female_count'] for r in analyzed_results)
    avg_bias = sum(r['bias_score'] for r in analyzed_results) / len(analyzed_results)
    
    male_biased = sum(1 for r in analyzed_results if r['bias_score'] > 0.1)
    female_biased = sum(1 for r in analyzed_results if r['bias_score'] < -0.1)
    neutral = sum(1 for r in analyzed_results if -0.1 <= r['bias_score'] <= 0.1)
    
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Total male pronouns across all texts: {total_male}")
    print(f"Total female pronouns across all texts: {total_female}")
    print(f"Average bias score: {avg_bias:+.3f}")
    print(f"\nTexts with male bias: {male_biased}")
    print(f"Texts with female bias: {female_biased}")
    print(f"Neutral texts: {neutral}")
    print("=" * 70)
    
    # Save summary
    summary_file = 'results/bias_summary.txt'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("BIAS ANALYSIS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total texts analyzed: {len(analyzed_results)}\n")
        f.write(f"Total male pronouns: {total_male}\n")
        f.write(f"Total female pronouns: {total_female}\n")
        f.write(f"Average bias score: {avg_bias:+.3f}\n\n")
        f.write(f"Texts with male bias: {male_biased}\n")
        f.write(f"Texts with female bias: {female_biased}\n")
        f.write(f"Neutral texts: {neutral}\n")
    
    print(f"\n✓ Summary saved to: {summary_file}")
    print("\n✓ Analysis complete! Check the results folder for detailed reports.")
else:
    print("\n" + "=" * 70)
    print("WARNING: No results to summarize!")
    print("=" * 70)