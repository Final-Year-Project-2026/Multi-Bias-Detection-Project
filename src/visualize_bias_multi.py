import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bias_detector import MultiBiasDetector
from collections import defaultdict
import numpy as np

print("=" * 70)
print("MULTI-BIAS VISUALIZATION")
print("=" * 70)

# Get bias type from command line
bias_type = sys.argv[1] if len(sys.argv) > 1 else 'combined'
print(f"\nVisualizing: {bias_type.upper()} BIAS\n")

# Determine which input file to use
if bias_type == 'gender':
    input_file = 'results/generated_outputs.txt'
elif bias_type == 'combined':
    input_file = 'results/generated_outputs_multi_bias.txt'
else:
    input_file = f'results/generated_outputs_{bias_type}.txt'

# Read and parse data
try:
    encodings = ['utf-8', 'latin-1', 'cp1252']
    content = None
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✓ File loaded with {encoding} encoding")
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
    'gender': {'male': 0, 'female': 0},
    'age': {'young': 0, 'old': 0},
    'socioeconomic': {'wealthy': 0, 'poor': 0},
    'regional': {'western': 0, 'eastern': 0},
    'sentiment': {'positive': 0, 'negative': 0}
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
            words = current_prompt.split()
            subject = " ".join(words[:2]).lower() if len(words) >= 2 else current_prompt[:20].lower()
            
            if bias_type == 'combined':
                results = detector.detect_all(current_output)
            else:
                results = {bias_type: detector.detect_single(current_output, bias_type)}
            
            for btype, result in results.items():
                if btype == 'gender':
                    subject_data[subject]['gender']['male'] += result['male_count']
                    subject_data[subject]['gender']['female'] += result['female_count']
                elif btype == 'age':
                    subject_data[subject]['age']['young'] += result['young_count']
                    subject_data[subject]['age']['old'] += result['old_count']
                elif btype == 'socioeconomic':
                    subject_data[subject]['socioeconomic']['wealthy'] += result['wealthy_count']
                    subject_data[subject]['socioeconomic']['poor'] += result['poor_count']
                elif btype == 'regional':
                    subject_data[subject]['regional']['western'] += result['western_count']
                    subject_data[subject]['regional']['eastern'] += result['eastern_count']
                elif btype == 'sentiment':
                    subject_data[subject]['sentiment']['positive'] += result['positive_count']
                    subject_data[subject]['sentiment']['negative'] += result['negative_count']
            
            current_prompt = None
            current_output = None

# Determine number of bias types to visualize
if bias_type == 'combined':
    bias_types_to_show = ['gender', 'age', 'socioeconomic', 'regional', 'sentiment']
else:
    bias_types_to_show = [bias_type]

# Create figure with subplots
num_plots = len(bias_types_to_show)
if num_plots <= 2:
    fig, axes = plt.subplots(1, num_plots, figsize=(8 * num_plots, 6))
    if num_plots == 1:
        axes = [axes]
else:
    rows = (num_plots + 1) // 2
    fig, axes = plt.subplots(rows, 2, figsize=(16, 6 * rows))
    axes = axes.flatten()

fig.suptitle(f'{bias_type.upper()} Bias Analysis', fontsize=16, fontweight='bold', y=0.995)

for idx, btype in enumerate(bias_types_to_show):
    ax = axes[idx]
    
    # Prepare data for this bias type
    subjects = []
    count1_list = []
    count2_list = []
    bias_scores = []
    
    for subject, data in subject_data.items():
        if btype == 'gender':
            count1 = data[btype]['male']
            count2 = data[btype]['female']
        elif btype == 'age':
            count1 = data[btype]['young']
            count2 = data[btype]['old']
        elif btype == 'socioeconomic':
            count1 = data[btype]['wealthy']
            count2 = data[btype]['poor']
        elif btype == 'regional':
            count1 = data[btype]['western']
            count2 = data[btype]['eastern']
        elif btype == 'sentiment':
            count1 = data[btype]['positive']
            count2 = data[btype]['negative']
        
        total = count1 + count2
        if total > 0:
            subjects.append(subject.title())
            count1_list.append(count1)
            count2_list.append(count2)
            bias = (count1 - count2) / total
            bias_scores.append(bias)
    
    # Sort by bias score
    if subjects:
        sorted_data = sorted(zip(subjects, count1_list, count2_list, bias_scores), 
                           key=lambda x: x[3], reverse=True)
        subjects, count1_list, count2_list, bias_scores = zip(*sorted_data)
        
        # Limit to top 15 for readability
        if len(subjects) > 15:
            subjects = subjects[:15]
            count1_list = count1_list[:15]
            count2_list = count2_list[:15]
            bias_scores = bias_scores[:15]
        
        x_pos = np.arange(len(subjects))
        
        # Set colors based on bias type
        if btype == 'gender':
            color1, color2 = '#4A90E2', '#E85D75'
            label1, label2 = 'Male', 'Female'
        elif btype == 'age':
            color1, color2 = '#FFA500', '#8B4513'
            label1, label2 = 'Young', 'Old'
        elif btype == 'socioeconomic':
            color1, color2 = '#FFD700', '#808080'
            label1, label2 = 'Wealthy', 'Poor'
        elif btype == 'regional':
            color1, color2 = '#0066CC', '#FF6600'
            label1, label2 = 'Western', 'Eastern'
        elif btype == 'sentiment':
            color1, color2 = '#2ECC71', '#E74C3C'
            label1, label2 = 'Positive', 'Negative'
        
        # Create stacked bar chart
        ax.bar(x_pos, count1_list, label=label1, color=color1, alpha=0.8)
        ax.bar(x_pos, count2_list, bottom=count1_list, label=label2, color=color2, alpha=0.8)
        
        ax.set_xlabel('Subject', fontsize=10, fontweight='bold')
        ax.set_ylabel('Count', fontsize=10, fontweight='bold')
        ax.set_title(f'{btype.upper()} Bias Distribution', fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(subjects, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
    else:
        ax.text(0.5, 0.5, f'No {btype} data available', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])

# Hide extra subplots if combined view has odd number
if num_plots < len(axes):
    for idx in range(num_plots, len(axes)):
        axes[idx].set_visible(False)

plt.tight_layout()

# Save figure
output_file = f'results/bias_visualization_{bias_type}.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualization saved to: {output_file}")

plt.show()

print("\nVisualization complete!")
print("\nUsage examples:")
print("  python src/visualize_bias_multi.py gender")
print("  python src/visualize_bias_multi.py age")
print("  python src/visualize_bias_multi.py combined")
