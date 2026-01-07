import re

print("=" * 70)
print("BIAS MITIGATION - POST-PROCESSING METHOD")
print("=" * 70)

# Read the original generated outputs
input_file = 'results/generated_outputs.txt'

try:
    encodings = ['utf-8', 'latin-1', 'cp1252']
    content = None
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"\n✓ File loaded with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"ERROR: Could not read {input_file}")
        exit()
        
except FileNotFoundError:
    print(f"ERROR: Could not find {input_file}")
    print("Please run generate_text.py first!")
    exit()

# Parse the file to extract prompts and outputs
lines = content.split('\n')
results = []
current_prompt = None
current_output = None

for line in lines:
    line = line.strip()
    if 'PROMPT:' in line.upper():
        current_prompt = line.split('PROMPT:', 1)[1].strip() if 'PROMPT:' in line.upper() else ""
    elif 'OUTPUT:' in line.upper():
        current_output = line.split('OUTPUT:', 1)[1].strip() if 'OUTPUT:' in line.upper() else ""
        if current_prompt and current_output:
            results.append({
                'prompt': current_prompt,
                'original_output': current_output
            })
            current_prompt = None
            current_output = None

print(f"✓ Loaded {len(results)} texts for post-processing\n")

# Define different debiasing strategies
def debias_replace_they(text):
    """Replace all gendered pronouns with 'they/them/their'"""
    # Replace he/she with they (case-insensitive)
    text = re.sub(r'\bhe\b', 'they', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'they', text, flags=re.IGNORECASE)
    
    # Replace him/her with them
    text = re.sub(r'\bhim\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'them', text, flags=re.IGNORECASE)
    
    # Replace his/hers with their
    text = re.sub(r'\bhis\b', 'their', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhers\b', 'theirs', text, flags=re.IGNORECASE)
    
    # Replace himself/herself with themselves
    text = re.sub(r'\bhimself\b', 'themselves', text, flags=re.IGNORECASE)
    text = re.sub(r'\bherself\b', 'themselves', text, flags=re.IGNORECASE)
    
    return text

def debias_remove_pronouns(text):
    """Remove gendered pronouns entirely (replace with profession/role)"""
    # This is a simple version - in real applications, you'd use NLP to identify the subject
    text = re.sub(r'\bhe\b', 'the person', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'the person', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhim\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhis\b', 'their', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhers\b', 'theirs', text, flags=re.IGNORECASE)
    return text

def debias_alternating(text, index):
    """Alternate between using 'he' and 'she' to balance"""
    # Simple strategy: use he for even indices, she for odd
    if index % 2 == 0:
        # Keep male pronouns, replace female with male
        text = re.sub(r'\bshe\b', 'he', text, flags=re.IGNORECASE)
        text = re.sub(r'\bher\b', 'his', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhers\b', 'his', text, flags=re.IGNORECASE)
        text = re.sub(r'\bherself\b', 'himself', text, flags=re.IGNORECASE)
    else:
        # Keep female pronouns, replace male with female
        text = re.sub(r'\bhe\b', 'she', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhim\b', 'her', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhis\b', 'her', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhimself\b', 'herself', text, flags=re.IGNORECASE)
    return text

# Apply all strategies
strategies = {
    'Replace with They/Them': debias_replace_they,
    'Remove Pronouns': debias_remove_pronouns,
    'Alternating Gender': debias_alternating
}

all_strategy_results = {}

print("=" * 70)
print("APPLYING POST-PROCESSING STRATEGIES")
print("=" * 70)

for strategy_name, strategy_func in strategies.items():
    print(f"\n{strategy_name}:")
    print("-" * 70)
    
    strategy_results = []
    
    for i, result in enumerate(results):
        original_text = result['original_output']
        
        # Apply debiasing
        if strategy_name == 'Alternating Gender':
            debiased_text = strategy_func(original_text, i)
        else:
            debiased_text = strategy_func(original_text)
        
        strategy_results.append({
            'prompt': result['prompt'],
            'original_text': original_text,
            'debiased_text': debiased_text
        })
        
        # Show example for first few
        if i < 3:
            print(f"\n  Example {i+1}:")
            print(f"    Original:  {original_text[:80]}...")
            print(f"    Debiased:  {debiased_text[:80]}...")
    
    all_strategy_results[strategy_name] = strategy_results
    print(f"\n✓ Processed {len(strategy_results)} texts")

# Save results for each strategy
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

for strategy_name, strategy_results in all_strategy_results.items():
    filename = strategy_name.lower().replace('/', '_').replace(' ', '_')
    output_file = f'results/post_processed_{filename}.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"POST-PROCESSING MITIGATION - {strategy_name.upper()}\n")
        f.write("=" * 70 + "\n\n")
        
        for i, result in enumerate(strategy_results, 1):
            f.write(f"{i}. PROMPT: {result['prompt']}\n")
            f.write(f"   ORIGINAL:  {result['original_text']}\n")
            f.write(f"   DEBIASED:  {result['debiased_text']}\n\n")
    
    print(f"✓ Saved: {output_file}")

# Analyze bias in post-processed outputs
print("\n" + "=" * 70)
print("ANALYZING BIAS IN POST-PROCESSED OUTPUTS")
print("=" * 70)

MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']

def count_pronouns(text):
    text_lower = text.lower()
    male_count = 0
    female_count = 0
    
    for pronoun in MALE_PRONOUNS:
        pattern = r'\b' + pronoun + r'\b'
        male_count += len(re.findall(pattern, text_lower))
    
    for pronoun in FEMALE_PRONOUNS:
        pattern = r'\b' + pronoun + r'\b'
        female_count += len(re.findall(pattern, text_lower))
    
    return male_count, female_count

def calculate_bias_score(male_count, female_count):
    total = male_count + female_count
    if total == 0:
        return 0.0
    return (male_count - female_count) / total

strategy_analysis = {}

for strategy_name, strategy_results in all_strategy_results.items():
    total_male_original = 0
    total_female_original = 0
    total_male_debiased = 0
    total_female_debiased = 0
    
    for result in strategy_results:
        male_orig, female_orig = count_pronouns(result['original_text'])
        male_deb, female_deb = count_pronouns(result['debiased_text'])
        
        total_male_original += male_orig
        total_female_original += female_orig
        total_male_debiased += male_deb
        total_female_debiased += female_deb
    
    bias_original = calculate_bias_score(total_male_original, total_female_original)
    bias_debiased = calculate_bias_score(total_male_debiased, total_female_debiased)
    
    strategy_analysis[strategy_name] = {
        'male_original': total_male_original,
        'female_original': total_female_original,
        'male_debiased': total_male_debiased,
        'female_debiased': total_female_debiased,
        'bias_original': bias_original,
        'bias_debiased': bias_debiased,
        'bias_reduction': abs(bias_original) - abs(bias_debiased)
    }
    
    print(f"\n{strategy_name}:")
    print(f"  ORIGINAL:  Male={total_male_original}, Female={total_female_original}, Bias={bias_original:+.3f}")
    print(f"  DEBIASED:  Male={total_male_debiased}, Female={total_female_debiased}, Bias={bias_debiased:+.3f}")
    print(f"  REDUCTION: {strategy_analysis[strategy_name]['bias_reduction']:+.3f}")
    
    if strategy_analysis[strategy_name]['bias_reduction'] > 0:
        print(f"  ✓ Bias REDUCED")
    elif strategy_analysis[strategy_name]['bias_reduction'] == 0:
        print(f"  → No change (bias eliminated completely!)")
    else:
        print(f"  ✗ Bias INCREASED")

# Save analysis report
analysis_file = 'results/mitigation_analysis_post_processing.txt'

with open(analysis_file, 'w', encoding='utf-8') as f:
    f.write("POST-PROCESSING MITIGATION ANALYSIS\n")
    f.write("=" * 70 + "\n\n")
    
    for strategy_name, analysis in strategy_analysis.items():
        f.write(f"{strategy_name}:\n")
        f.write("-" * 70 + "\n")
        f.write(f"ORIGINAL STATISTICS:\n")
        f.write(f"  Male pronouns: {analysis['male_original']}\n")
        f.write(f"  Female pronouns: {analysis['female_original']}\n")
        f.write(f"  Bias score: {analysis['bias_original']:+.3f}\n\n")
        
        f.write(f"DEBIASED STATISTICS:\n")
        f.write(f"  Male pronouns: {analysis['male_debiased']}\n")
        f.write(f"  Female pronouns: {analysis['female_debiased']}\n")
        f.write(f"  Bias score: {analysis['bias_debiased']:+.3f}\n\n")
        
        f.write(f"IMPROVEMENT:\n")
        f.write(f"  Bias reduction: {analysis['bias_reduction']:+.3f}\n")
        reduction_percent = (analysis['bias_reduction'] / abs(analysis['bias_original']) * 100) if analysis['bias_original'] != 0 else 100
        f.write(f"  Reduction percentage: {reduction_percent:.1f}%\n\n")
        f.write("=" * 70 + "\n\n")

print(f"\n✓ Analysis saved to: {analysis_file}")

print("\n" + "=" * 70)
print("POST-PROCESSING MITIGATION COMPLETE!")
print("=" * 70)
print("\nBoth mitigation methods are now complete!")
print("Check the results folder for all generated files.")