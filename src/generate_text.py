# Import required libraries
from transformers import pipeline
import time

# This prints a message so you know the program started
print("Starting AI text generation...")
print("Loading the AI model (this takes 1-2 minutes first time)...")

# Load the AI model
# GPT-2 is a free, open-source language model
generator = pipeline('text-generation', model='gpt2')

print("Model loaded successfully!")
print("-" * 50)

# Read the prompts from our file
prompts_file = 'data/test_prompts.txt'

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
        # Generate text
        output = generator(
            prompt,
            max_length=30,        # Maximum length of generated text
            num_return_sequences=1,  # Generate 1 completion
            temperature=0.7,      # Controls randomness (0.7 is moderate)
            do_sample=True        # Enable random sampling
        )
        
        # Extract the generated text
        generated = output[0]['generated_text']
        
        print(f"   Result: {generated}")
        
        # Save the result
        all_results.append({
            'prompt': prompt,
            'generated_text': generated
        })
        
        # Small delay to avoid overwhelming your computer
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ERROR: {e}")
        continue

print("\n" + "=" * 50)
print(f"COMPLETED! Generated text for {len(all_results)} prompts")
print("=" * 50)

# Save results to a file WITH PROPER ENCODING
output_file = 'results/generated_outputs.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("BIAS DETECTION PROJECT - GENERATED TEXTS\n")
    f.write("=" * 70 + "\n\n")
    
    for i, result in enumerate(all_results, 1):
        f.write(f"{i}. PROMPT: {result['prompt']}\n")
        f.write(f"   OUTPUT: {result['generated_text']}\n\n")

print(f"\nResults saved to: {output_file}")
print("You can now open this file to see all generated texts!")