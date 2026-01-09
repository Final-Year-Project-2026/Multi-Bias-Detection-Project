# Import required libraries
import openai
import time
import sys
import os

# This prints a message so you know the program started
print("=" * 70)
print("MULTI-BIAS AI TEXT GENERATION (GPT-4o-mini)")
print("=" * 70)

# Get bias type from command line or use combined
bias_type = sys.argv[1] if len(sys.argv) > 1 else 'combined'

print(f"\nBias Type: {bias_type.upper()}")

# Set up OpenAI API
# Make sure to set your API key as an environment variable: OPENAI_API_KEY
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    print("ERROR: OpenAI API key not found!")
    print("Please set your API key:")
    print("  Windows: set OPENAI_API_KEY=your-key-here")
    print("  Linux/Mac: export OPENAI_API_KEY=your-key-here")
    exit()

print("✓ OpenAI API key configured")
print("Using GPT-4o-mini for high-quality text generation")
print("-" * 50)

# Determine which prompts file to use
if bias_type == 'gender':
    prompts_file = 'data/test_prompts.txt'
elif bias_type == 'age':
    prompts_file = 'data/test_prompts_age.txt'
elif bias_type == 'socioeconomic':
    prompts_file = 'data/test_prompts_socioeconomic.txt'
elif bias_type == 'regional':
    prompts_file = 'data/test_prompts_regional.txt'
elif bias_type == 'sentiment':
    prompts_file = 'data/test_prompts_sentiment.txt'
elif bias_type == 'combined':
    prompts_file = 'data/test_prompts_combined.txt'
else:
    print(f"ERROR: Unknown bias type '{bias_type}'")
    print("Valid types: gender, age, socioeconomic, regional, sentiment, combined")
    exit()

try:
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"Loaded {len(prompts)} prompts from file")
    print("-" * 50)
    
except FileNotFoundError:
    print(f"ERROR: Could not find {prompts_file}")
    print("Make sure you created the test_prompts.txt file in the data folder")
    exit()

# Generate text for each prompt
all_results = []

for i, prompt in enumerate(prompts, 1):
    print(f"\n[{i}/{len(prompts)}] Generating for: {prompt}")
    
    try:
        # Generate text using GPT-4o-mini
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a text completion assistant. Complete the given text naturally and coherently in 2-4 sentences. Generate realistic, detailed content that may contain implicit biases for analysis purposes."
                },
                {
                    "role": "user", 
                    "content": f"Complete this text naturally: {prompt}"
                }
            ],
            max_tokens=150,
            temperature=0.8,
            n=1
        )
        
        # Extract the generated text
        completion = response.choices[0].message.content.strip()
        
        # Remove duplicate prompt from start of completion if present
        prompt_lower = prompt.lower().strip()
        completion_lower = completion.lower()
        if completion_lower.startswith(prompt_lower):
            completion = completion[len(prompt):].strip()
        
        generated_text = prompt + " " + completion
        
        print(f"   Result: {generated_text}")
        
        # Save the result
        all_results.append({
            'prompt': prompt,
            'generated_text': generated_text
        })
        
        # Small delay to respect API rate limits
        time.sleep(1)
        
    except Exception as e:
        print(f"   ERROR: {e}")
        continue

print("=" * 50)
print(f"COMPLETED! Generated text for {len(all_results)} prompts")
print("=" * 50)

# Save results to a file WITH PROPER ENCODING
# Create filename based on bias type
if bias_type == 'combined':
    output_file = 'results/generated_outputs_multi_bias.txt'
else:
    output_file = f'results/generated_outputs_{bias_type}.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"BIAS DETECTION PROJECT - GENERATED TEXTS ({bias_type.upper()})\n")
    f.write("=" * 70 + "\n\n")
    
    for i, result in enumerate(all_results, 1):
        f.write(f"{i}. PROMPT: {result['prompt']}\n")
        f.write(f"   OUTPUT: {result['generated_text']}\n\n")

print(f"\nResults saved to: {output_file}")
print("You can now open this file to see all generated texts!")
print("\nUsage examples:")
print("  python src/generate_text.py gender")
print("  python src/generate_text.py age")
print("  python src/generate_text.py combined")