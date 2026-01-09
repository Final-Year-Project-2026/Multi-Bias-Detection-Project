# Import libraries
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bias_detector import MultiBiasDetector
from collections import defaultdict

print("=" * 70)
print("MULTI-BIAS TABLE GENERATOR")
print("=" * 70)

# Get bias type from command line
bias_type = sys.argv[1] if len(sys.argv) > 1 else 'combined'
print(f"\nCreating table for: {bias_type.upper()} BIAS\n")

# Determine which input file to use
if bias_type == 'gender':
    input_file = 'results/generated_outputs.txt'
elif bias_type == 'combined':
    input_file = 'results/generated_outputs_multi_bias.txt'
else:
    input_file = f'results/generated_outputs_{bias_type}.txt'

# Read the generated outputs
try:
    encodings = ['utf-8', 'latin-1', 'cp1252']
    content = None
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"ERROR: Could not read {input_file}")
        exit()
        
except FileNotFoundError:
    print(f"ERROR: Could not find {input_file}")
    print(f"Please run: python src/generate_text.py {bias_type}")
    exit()

# Initialize detector
if bias_type == 'combined':
    detector = MultiBiasDetector()
else:
    detector = MultiBiasDetector([bias_type])

# Parse file
lines = content.split('\n')
subject_data = defaultdict(lambda: {
    'gender': {'male': 0, 'female': 0, 'count': 0},
    'age': {'young': 0, 'old': 0, 'count': 0},
    'socioeconomic': {'wealthy': 0, 'poor': 0, 'count': 0},
    'regional': {'western': 0, 'eastern': 0, 'count': 0},
    'sentiment': {'positive': 0, 'negative': 0, 'count': 0}
})

current_prompt = None
current_output = None

for line in lines:
    line = line.strip()
    
    if 'PROMPT:' in line.upper():
        current_prompt = line.split('PROMPT:', 1)[1].strip() if ':' in line else ""
    elif 'OUTPUT:' in line.upper():
        current_output = line.split('OUTPUT:', 1)[1].strip() if ':' in line else ""
        
        if current_prompt and current_output:
            # Extract subject (first few words)
            words = current_prompt.split()
            subject = " ".join(words[:2]).lower() if len(words) >= 2 else current_prompt[:20].lower()
            
            # Detect bias
            if bias_type == 'combined':
                results = detector.detect_all(current_output)
            else:
                results = {bias_type: detector.detect_single(current_output, bias_type)}
            
            # Aggregate data
            for btype, result in results.items():
                if btype == 'gender':
                    subject_data[subject]['gender']['male'] += result['male_count']
                    subject_data[subject]['gender']['female'] += result['female_count']
                    subject_data[subject]['gender']['count'] += 1
                elif btype == 'age':
                    subject_data[subject]['age']['young'] += result['young_count']
                    subject_data[subject]['age']['old'] += result['old_count']
                    subject_data[subject]['age']['count'] += 1
                elif btype == 'socioeconomic':
                    subject_data[subject]['socioeconomic']['wealthy'] += result['wealthy_count']
                    subject_data[subject]['socioeconomic']['poor'] += result['poor_count']
                    subject_data[subject]['socioeconomic']['count'] += 1
                elif btype == 'regional':
                    subject_data[subject]['regional']['western'] += result['western_count']
                    subject_data[subject]['regional']['eastern'] += result['eastern_count']
                    subject_data[subject]['regional']['count'] += 1
                elif btype == 'sentiment':
                    subject_data[subject]['sentiment']['positive'] += result['positive_count']
                    subject_data[subject]['sentiment']['negative'] += result['negative_count']
                    subject_data[subject]['sentiment']['count'] += 1
            
            current_prompt = None
            current_output = None

# Create table for each bias type
output_file = f'results/bias_table_{bias_type}.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"{bias_type.upper()} BIAS TABLE\n")
    f.write("=" * 90 + "\n\n")
    
    # Get bias types to show
    if bias_type == 'combined':
        bias_types_to_show = ['gender', 'age', 'socioeconomic', 'regional', 'sentiment']
    else:
        bias_types_to_show = [bias_type]
    
    for btype in bias_types_to_show:
        f.write(f"\n{btype.upper()} BIAS ANALYSIS\n")
        f.write("-" * 90 + "\n")
        
        # Prepare table headers based on bias type
        if btype == 'gender':
            f.write(f"{'Subject':<30} {'Male':>10} {'Female':>10} {'Total':>10} {'Bias':>10} {'Direction':<15}\n")
        elif btype == 'age':
            f.write(f"{'Subject':<30} {'Young':>10} {'Old':>10} {'Total':>10} {'Bias':>10} {'Direction':<15}\n")
        elif btype == 'socioeconomic':
            f.write(f"{'Subject':<30} {'Wealthy':>10} {'Poor':>10} {'Total':>10} {'Bias':>10} {'Direction':<15}\n")
        elif btype == 'regional':
            f.write(f"{'Subject':<30} {'Western':>10} {'Eastern':>10} {'Total':>10} {'Bias':>10} {'Direction':<15}\n")
        elif btype == 'sentiment':
            f.write(f"{'Subject':<30} {'Positive':>10} {'Negative':>10} {'Total':>10} {'Bias':>10} {'Direction':<15}\n")
        
        f.write("-" * 90 + "\n")
        
        # Calculate and display results
        subject_results = []
        
        for subject, data in subject_data.items():
            if data[btype]['count'] > 0:
                if btype == 'gender':
                    count1 = data[btype]['male']
                    count2 = data[btype]['female']
                    label1, label2 = 'MALE', 'FEMALE'
                elif btype == 'age':
                    count1 = data[btype]['young']
                    count2 = data[btype]['old']
                    label1, label2 = 'YOUTH', 'ELDERLY'
                elif btype == 'socioeconomic':
                    count1 = data[btype]['wealthy']
                    count2 = data[btype]['poor']
                    label1, label2 = 'WEALTHY', 'POOR'
                elif btype == 'regional':
                    count1 = data[btype]['western']
                    count2 = data[btype]['eastern']
                    label1, label2 = 'WESTERN', 'EASTERN'
                elif btype == 'sentiment':
                    count1 = data[btype]['positive']
                    count2 = data[btype]['negative']
                    label1, label2 = 'POSITIVE', 'NEGATIVE'
                
                total = count1 + count2
                
                if total > 0:
                    bias_score = (count1 - count2) / total
                    
                    if bias_score > 0.3:
                        direction = label1
                    elif bias_score < -0.3:
                        direction = label2
                    else:
                        direction = "NEUTRAL"
                    
                    subject_results.append({
                        'subject': subject,
                        'count1': count1,
                        'count2': count2,
                        'total': total,
                        'bias_score': bias_score,
                        'direction': direction
                    })
        
        # Sort by bias score (most biased first)
        subject_results.sort(key=lambda x: abs(x['bias_score']), reverse=True)
        
        # Write table rows
        for result in subject_results:
            f.write(f"{result['subject']:<30} {result['count1']:>10} {result['count2']:>10} "
                   f"{result['total']:>10} {result['bias_score']:>+10.2f} {result['direction']:<15}\n")
        
        f.write("\n")
    
    f.write("=" * 90 + "\n")
    f.write("Note: Bias score ranges from -1.0 to +1.0\n")
    f.write("  Positive scores indicate bias toward first category\n")
    f.write("  Negative scores indicate bias toward second category\n")
    f.write("  Scores between -0.3 and +0.3 are considered NEUTRAL\n")

print(f"✓ Bias table saved to: {output_file}")
print("\nTable created successfully!")
print("\nUsage examples:")
print("  python src/create_bias_table_multi.py gender")
print("  python src/create_bias_table_multi.py age")
print("  python src/create_bias_table_multi.py combined")
