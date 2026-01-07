from transformers import pipeline
import time
import re

print("=" * 70)
print("BIAS MITIGATION - PROMPT ENGINEERING METHOD")
print("=" * 70)

# Load the AI model
print("\nLoading AI model...")
generator = pipeline('text-generation', model='gpt2')
print("✓ Model loaded successfully!")

# Read the original prompts
prompts_file = 'data/test_prompts.txt'

try:
    with open(prompts_file, 'r', encoding='utf-8') as f:
        original_prompts = [line.strip() for line in f.readlines() if line.strip()]
    print(f"✓ Loaded {len(original_prompts)} prompts\n")
except FileNotFoundError:
    print(f"ERROR: Could not find {prompts_file}")
    exit()

# Define debiasing strategies
def add_debiasing_instruction_v1(prompt):
    """Add explicit instruction to avoid gender bias"""
    return f"{prompt} [Continue without making gender assumptions or using gendered pronouns]"

def add_debiasing_instruction_v2(prompt):
    """Alternative debiasing instruction"""
    return f"{prompt} [Use gender-neutral language]"

def add_debiasing_instruction_v3(prompt):
    """Another alternative"""
    return f"Write inclusively and without gender stereotypes: {prompt}"

# We'll test all three strategies
debiasing_strategies = {
    'Strategy 1': add_debiasing_instruction_v1,
    'Strategy 2': add_debiasing_instruction_v2,
    'Strategy 3': add_debiasing_instruction_v3
}

# Store results for each strategy
all_strategy_results = {}

print("=" * 70)
print("GENERATING DEBIASED TEXT WITH DIFFERENT STRATEGIES")
print("=" * 70)

for strategy_name, strategy_func in debiasing_strategies.items():
    print(f"\n{'='*70}")
    print(f"Testing: {strategy_name}")
    print(f"{'='*70}\n")
    
    strategy_results = []
    
    for i, original_prompt in enumerate(original_prompts, 1):
        # Create debiased prompt
        debiased_prompt = strategy_func(original_prompt)
        
        print(f"[{i}/{len(original_prompts)}] Generating for: {original_prompt}")
        print(f"   Modified prompt: {debiased_prompt[:80]}...")
        
        try:
            # Generate text with debiased prompt
            output = generator(
                debiased_prompt,
                max_length=40,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            
            generated = output[0]['generated_text']
            
            # Remove the instruction part from output for cleaner results
            # Try to extract just the completion after the original prompt
            if original_prompt in generated:
                generated = generated.replace(original_prompt, original_prompt)
            
            print(f"   Result: {generated[:100]}...")
            
            strategy_results.append({
                'original_prompt': original_prompt,
                'debiased_prompt': debiased_prompt,
                'generated_text': generated
            })
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ERROR: {e}")
            continue
    
    all_strategy_results[strategy_name] = strategy_results
    print(f"\n✓ {strategy_name} complete: Generated {len(strategy_results)} texts")

print("\n" + "=" * 70)
print("ALL STRATEGIES COMPLETED")
print("=" * 70)

# Save results for each strategy
for strategy_name, results in all_strategy_results.items():
    # Create filename
    filename = strategy_name.lower().replace(' ', '_')
    output_file = f'results/mitigated_{filename}.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"BIAS MITIGATION - {strategy_name.upper()}\n")
        f.write("=" * 70 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. ORIGINAL PROMPT: {result['original_prompt']}\n")
            f.write(f"   DEBIASED PROMPT: {result['debiased_prompt']}\n")
            f.write(f"   OUTPUT: {result['generated_text']}\n\n")
    
    print(f"✓ {strategy_name} results saved to: {output_file}")

# Function to count pronouns (reused from analyze_bias.py)
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

# Analyze bias in mitigated outputs
print("\n" + "=" * 70)
print("ANALYZING BIAS IN MITIGATED OUTPUTS")
print("=" * 70)

strategy_analysis = {}

for strategy_name, results in all_strategy_results.items():
    total_male = 0
    total_female = 0
    bias_scores = []
    
    for result in results:
        male, female = count_pronouns(result['generated_text'])
        total_male += male
        total_female += female
        
        bias = calculate_bias_score(male, female)
        bias_scores.append(bias)
    
    avg_bias = sum(bias_scores) / len(bias_scores) if bias_scores else 0
    
    strategy_analysis[strategy_name] = {
        'total_male': total_male,
        'total_female': total_female,
        'average_bias': avg_bias,
        'texts_generated': len(results)
    }
    
    print(f"\n{strategy_name}:")
    print(f"  Total male pronouns: {total_male}")
    print(f"  Total female pronouns: {total_female}")
    print(f"  Average bias score: {avg_bias:+.3f}")
    print(f"  Texts generated: {len(results)}")

# Load original results for comparison
print("\n" + "=" * 70)
print("COMPARING WITH ORIGINAL (BASELINE) RESULTS")
print("=" * 70)

try:
    with open('results/bias_summary.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        # Extract original stats (this is a simple parsing)
        for line in content.split('\n'):
            if 'Total male pronouns:' in line:
                original_male = int(line.split(':')[1].strip())
            elif 'Total female pronouns:' in line:
                original_female = int(line.split(':')[1].strip())
            elif 'Average bias score:' in line:
                original_bias = float(line.split(':')[1].strip())
    
    print(f"\nORIGINAL (Before mitigation):")
    print(f"  Total male pronouns: {original_male}")
    print(f"  Total female pronouns: {original_female}")
    print(f"  Average bias score: {original_bias:+.3f}")
    
    print("\n" + "-" * 70)
    print("BIAS REDUCTION COMPARISON")
    print("-" * 70)
    
    for strategy_name, analysis in strategy_analysis.items():
        bias_reduction = abs(original_bias) - abs(analysis['average_bias'])
        reduction_percent = (bias_reduction / abs(original_bias) * 100) if original_bias != 0 else 0
        
        print(f"\n{strategy_name}:")
        print(f"  Bias reduction: {bias_reduction:+.3f}")
        print(f"  Reduction percentage: {reduction_percent:.1f}%")
        
        if bias_reduction > 0:
            print(f"  ✓ This strategy REDUCED bias!")
        elif bias_reduction < 0:
            print(f"  ✗ This strategy INCREASED bias (not good)")
        else:
            print(f"  → No change in bias")
    
except FileNotFoundError:
    print("Could not find original bias_summary.txt for comparison")

# Save comparison report
comparison_file = 'results/mitigation_comparison_prompt_engineering.txt'

with open(comparison_file, 'w', encoding='utf-8') as f:
    f.write("BIAS MITIGATION COMPARISON - PROMPT ENGINEERING\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("ORIGINAL (BASELINE) RESULTS:\n")
    f.write(f"  Total male pronouns: {original_male}\n")
    f.write(f"  Total female pronouns: {original_female}\n")
    f.write(f"  Average bias score: {original_bias:+.3f}\n\n")
    
    f.write("MITIGATION RESULTS:\n")
    f.write("-" * 70 + "\n")
    
    for strategy_name, analysis in strategy_analysis.items():
        bias_reduction = abs(original_bias) - abs(analysis['average_bias'])
        reduction_percent = (bias_reduction / abs(original_bias) * 100) if original_bias != 0 else 0
        
        f.write(f"\n{strategy_name}:\n")
        f.write(f"  Total male pronouns: {analysis['total_male']}\n")
        f.write(f"  Total female pronouns: {analysis['total_female']}\n")
        f.write(f"  Average bias score: {analysis['average_bias']:+.3f}\n")
        f.write(f"  Bias reduction: {bias_reduction:+.3f}\n")
        f.write(f"  Reduction percentage: {reduction_percent:.1f}%\n")

print(f"\n✓ Comparison report saved to: {comparison_file}")

print("\n" + "=" * 70)
print("PROMPT ENGINEERING MITIGATION COMPLETE!")
print("=" * 70)
print("\nNext step: Run post-processing mitigation (mitigate_post_processing.py)")
print("This will give you a second mitigation method to compare!")