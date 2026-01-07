import matplotlib.pyplot as plt
import re
from collections import defaultdict

print("Creating bias visualization...\n")

# Read and parse data
input_file = 'results/generated_outputs.txt'

try:
    # Try multiple encodings
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
    exit()

MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']

def count_pronouns(text):
    text_lower = text.lower()
    male_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) for p in MALE_PRONOUNS)
    female_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) for p in FEMALE_PRONOUNS)
    return male_count, female_count

# Parse and collect data
profession_data = defaultdict(lambda: {'male': 0, 'female': 0})
lines = content.split('\n')
current_prompt = None
current_output = None

for line in lines:
    line = line.strip()
    if 'PROMPT:' in line.upper():
        current_prompt = line.split('PROMPT:', 1)[1].strip() if 'PROMPT:' in line.upper() else ""
    elif 'OUTPUT:' in line.upper():
        current_output = line.split('OUTPUT:', 1)[1].strip() if 'OUTPUT:' in line.upper() else ""
        if current_prompt and current_output:
            words = current_prompt.split()
            if len(words) >= 2 and words[0].lower() == "the":
                profession = words[1].lower()
                male, female = count_pronouns(current_output)
                profession_data[profession]['male'] += male
                profession_data[profession]['female'] += female
            current_prompt = None
            current_output = None

# Prepare data for plotting
professions = []
male_counts = []
female_counts = []
bias_scores = []

for profession, data in sorted(profession_data.items()):
    total = data['male'] + data['female']
    if total > 0:  # Only include professions with pronouns
        professions.append(profession.capitalize())
        male_counts.append(data['male'])
        female_counts.append(data['female'])
        bias = (data['male'] - data['female']) / total
        bias_scores.append(bias)

print(f"✓ Found {len(professions)} professions with pronouns")

# Sort by bias score for better visualization
sorted_data = sorted(zip(professions, male_counts, female_counts, bias_scores), 
                     key=lambda x: x[3], reverse=True)
professions, male_counts, female_counts, bias_scores = zip(*sorted_data)

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Stacked bar chart of pronoun counts
x_pos = range(len(professions))
ax1.bar(x_pos, male_counts, label='Male Pronouns', color='#4A90E2', alpha=0.8)
ax1.bar(x_pos, female_counts, bottom=male_counts, label='Female Pronouns', 
        color='#E85D75', alpha=0.8)
ax1.set_xlabel('Profession', fontsize=12, fontweight='bold')
ax1.set_ylabel('Pronoun Count', fontsize=12, fontweight='bold')
ax1.set_title('Male vs Female Pronouns by Profession', fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(professions, rotation=45, ha='right')
ax1.legend(loc='upper right', framealpha=0.9)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

# Plot 2: Bias score bar chart
colors = ['#4A90E2' if score > 0 else '#E85D75' if score < 0 else '#95A5A6' 
          for score in bias_scores]
bars = ax2.bar(x_pos, bias_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

# Add a horizontal line at y=0
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1.5)

# Add threshold lines
ax2.axhline(y=0.3, color='#4A90E2', linestyle='--', linewidth=1, alpha=0.5, label='Male bias threshold')
ax2.axhline(y=-0.3, color='#E85D75', linestyle='--', linewidth=1, alpha=0.5, label='Female bias threshold')

ax2.set_xlabel('Profession', fontsize=12, fontweight='bold')
ax2.set_ylabel('Bias Score', fontsize=12, fontweight='bold')
ax2.set_title('Gender Bias Score by Profession\n(+1 = Male biased, -1 = Female biased, 0 = Neutral)', 
              fontsize=14, fontweight='bold', pad=20)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(professions, rotation=45, ha='right')
ax2.set_ylim(-1.2, 1.2)
ax2.legend(loc='upper right', framealpha=0.9)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.set_axisbelow(True)

# Add value labels on bars for bias scores
for i, (bar, score) in enumerate(zip(bars, bias_scores)):
    height = bar.get_height()
    if abs(height) > 0.1:  # Only show labels for significant bias
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{score:.2f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('results/bias_visualization.png', dpi=300, bbox_inches='tight')
print("\n✓ Chart saved to: results/bias_visualization.png")

# Create a second figure - pie chart showing overall distribution
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart 1: Total pronoun distribution
total_male = sum(male_counts)
total_female = sum(female_counts)
ax3.pie([total_male, total_female], 
        labels=['Male Pronouns', 'Female Pronouns'],
        colors=['#4A90E2', '#E85D75'],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'})
ax3.set_title('Overall Pronoun Distribution', fontsize=14, fontweight='bold', pad=20)

# Pie chart 2: Bias direction distribution
male_biased = sum(1 for s in bias_scores if s > 0.3)
female_biased = sum(1 for s in bias_scores if s < -0.3)
neutral = sum(1 for s in bias_scores if -0.3 <= s <= 0.3)

ax4.pie([male_biased, female_biased, neutral],
        labels=[f'Male Biased\n({male_biased} professions)',
                f'Female Biased\n({female_biased} professions)',
                f'Neutral\n({neutral} professions)'],
        colors=['#4A90E2', '#E85D75', '#95A5A6'],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'})
ax4.set_title('Profession Bias Distribution', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('results/bias_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Distribution chart saved to: results/bias_distribution.png")

print("\n" + "=" * 70)
print("VISUALIZATION SUMMARY")
print("=" * 70)
print(f"Total male pronouns: {total_male}")
print(f"Total female pronouns: {total_female}")
print(f"Male bias percentage: {(total_male/(total_male+total_female)*100):.1f}%")
print(f"Female bias percentage: {(total_female/(total_male+total_female)*100):.1f}%")
print(f"\nProfessions with male bias: {male_biased}")
print(f"Professions with female bias: {female_biased}")
print(f"Neutral professions: {neutral}")
print("=" * 70)

print("\n✓ Visualization complete!")
print("✓ Open the PNG files in the results folder to see your charts.")
print("\nThe charts will also be displayed now...")

# Show the plots
plt.show()