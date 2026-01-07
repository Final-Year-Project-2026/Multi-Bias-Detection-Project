import matplotlib.pyplot as plt

print("=" * 70)
print("COMPREHENSIVE MITIGATION COMPARISON")
print("=" * 70)

# Read bias summary for original baseline
try:
    with open('results/bias_summary.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        for line in content.split('\n'):
            if 'Total male pronouns:' in line:
                baseline_male = int(line.split(':')[1].strip())
            elif 'Total female pronouns:' in line:
                baseline_female = int(line.split(':')[1].strip())
            elif 'Average bias score:' in line:
                baseline_bias = float(line.split(':')[1].strip())
except:
    print("ERROR: Could not load baseline results")
    exit()

print(f"\nBASELINE (No mitigation):")
print(f"  Male pronouns: {baseline_male}")
print(f"  Female pronouns: {baseline_female}")
print(f"  Bias score: {baseline_bias:+.3f}")

# Collect results from all methods
methods = {
    'Baseline (No mitigation)': {
        'bias_score': baseline_bias,
        'male': baseline_male,
        'female': baseline_female
    }
}

# Try to load prompt engineering results
try:
    with open('results/mitigation_comparison_prompt_engineering.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        # Parse each strategy (this is simplified parsing)
        current_strategy = None
        for line in content.split('\n'):
            if line.strip() and line.strip().endswith(':') and 'Strategy' in line:
                current_strategy = line.strip()[:-1]
            elif current_strategy and 'Average bias score:' in line:
                bias = float(line.split(':')[1].strip())
                methods[f'Prompt: {current_strategy}'] = {'bias_score': bias, 'male': 0, 'female': 0}
except:
    print("\nWarning: Could not load prompt engineering results")

# Try to load post-processing results
try:
    with open('results/mitigation_analysis_post_processing.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        sections = content.split('=' * 70)
        for section in sections:
            if 'Replace with They/Them:' in section:
                for line in section.split('\n'):
                    if 'Bias score:' in line and 'DEBIASED' in section[:section.index(line)]:
                        bias = float(line.split(':')[1].strip())
                        methods['Post-process: Replace with They/Them'] = {'bias_score': bias, 'male': 0, 'female': 0}
            elif 'Remove Pronouns:' in section:
                for line in section.split('\n'):
                    if 'Bias score:' in line and 'DEBIASED' in section[:section.index(line)]:
                        bias = float(line.split(':')[1].strip())
                        methods['Post-process: Remove Pronouns'] = {'bias_score': bias, 'male': 0, 'female': 0}
            elif 'Alternating Gender:' in section:
                for line in section.split('\n'):
                    if 'Bias score:' in line and 'DEBIASED' in section[:section.index(line)]:
                        bias = float(line.split(':')[1].strip())
                        methods['Post-process: Alternating'] = {'bias_score': bias, 'male': 0, 'female': 0}
except:
    print("Warning: Could not load post-processing results")

# Display comparison
print("\n" + "=" * 70)
print("METHOD COMPARISON")
print("=" * 70)

for method_name, data in methods.items():
    bias_reduction = abs(baseline_bias) - abs(data['bias_score'])
    reduction_percent = (bias_reduction / abs(baseline_bias) * 100) if baseline_bias != 0 else 0
    
    print(f"\n{method_name}:")
    print(f"  Bias score: {data['bias_score']:+.3f}")
    print(f"  Reduction from baseline: {bias_reduction:+.3f} ({reduction_percent:.1f}%)")

# Create visualization
method_names = list(methods.keys())
bias_scores = [methods[m]['bias_score'] for m in method_names]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Bias scores comparison
colors = ['#E74C3C' if abs(score) > 0.3 else '#F39C12' if abs(score) > 0.1 else '#2ECC71' 
          for score in bias_scores]
bars = ax1.bar(range(len(method_names)), bias_scores, color=colors, alpha=0.8, edgecolor='black')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax1.axhline(y=0.3, color='red', linestyle='--', linewidth=1, alpha=0.3, label='High bias threshold')
ax1.axhline(y=-0.3, color='red', linestyle='--', linewidth=1, alpha=0.3)
ax1.set_xlabel('Mitigation Method', fontsize=12, fontweight='bold')
ax1.set_ylabel('Bias Score', fontsize=12, fontweight='bold')
ax1.set_title('Bias Score by Mitigation Method\n(Lower absolute value = Better)', 
              fontsize=14, fontweight='bold', pad=20)
ax1.set_xticks(range(len(method_names)))
ax1.set_xticklabels(method_names, rotation=45, ha='right', fontsize=9)
ax1.set_ylim(-1, 1)
ax1.grid(axis='y', alpha=0.3)
ax1.legend()

# Add value labels on bars
for i, (bar, score) in enumerate(zip(bars, bias_scores)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{score:.3f}',
            ha='center', va='bottom' if height > 0 else 'top',
            fontsize=9, fontweight='bold')

# Plot 2: Bias reduction comparison
baseline_abs_bias = abs(baseline_bias)
bias_reductions = [baseline_abs_bias - abs(score) for score in bias_scores]
colors2 = ['#2ECC71' if red > 0 else '#E74C3C' for red in bias_reductions]
bars2 = ax2.bar(range(len(method_names)), bias_reductions, color=colors2, alpha=0.8, edgecolor='black')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax2.set_xlabel('Mitigation Method', fontsize=12, fontweight='bold')
ax2.set_ylabel('Bias Reduction', fontsize=12, fontweight='bold')
ax2.set_title('Bias Reduction by Method\n(Positive = Good, Negative = Bad)', 
              fontsize=14, fontweight='bold', pad=20)
ax2.set_xticks(range(len(method_names)))
ax2.set_xticklabels(method_names, rotation=45, ha='right', fontsize=9)
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bar, reduction in zip(bars2, bias_reductions):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{reduction:.3f}',
            ha='center', va='bottom' if height > 0 else 'top',
            fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('results/mitigation_comparison_all_methods.png', dpi=300, bbox_inches='tight')
print("\n✓ Comparison chart saved to: results/mitigation_comparison_all_methods.png")

# Create summary report
summary_file = 'results/final_mitigation_summary.txt'

with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("FINAL MITIGATION SUMMARY - ALL METHODS\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"BASELINE (No mitigation):\n")
    f.write(f"  Bias score: {baseline_bias:+.3f}\n\n")
    
    f.write("RESULTS BY METHOD:\n")
    f.write("-" * 70 + "\n\n")
    
    # Sort by best performance
    sorted_methods = sorted(methods.items(), key=lambda x: abs(x[1]['bias_score']))
    
    for rank, (method_name, data) in enumerate(sorted_methods, 1):
        bias_reduction = abs(baseline_bias) - abs(data['bias_score'])
        reduction_percent = (bias_reduction / abs(baseline_bias) * 100) if baseline_bias != 0 else 100
        
        f.write(f"{rank}. {method_name}\n")
        f.write(f"   Bias score: {data['bias_score']:+.3f}\n")
        f.write(f"   Bias reduction: {bias_reduction:+.3f}\n")
        f.write(f"   Reduction percentage: {reduction_percent:.1f}%\n")
        
        if abs(data['bias_score']) < 0.1:
            f.write(f"   Rating: ★★★★★ Excellent - Near zero bias\n")
        elif abs(data['bias_score']) < 0.2:
            f.write(f"   Rating: ★★★★☆ Very Good - Low bias\n")
        elif abs(data['bias_score']) < 0.3:
            f.write(f"   Rating: ★★★☆☆ Good - Moderate bias\n")
        else:
            f.write(f"   Rating: ★★☆☆☆ Fair - Still significant bias\n")
        
        f.write("\n")
    
    f.write("=" * 70 + "\n")
    f.write("RECOMMENDATION:\n")
    best_method = sorted_methods[0][0]
    f.write(f"Best performing method: {best_method}\n")
    f.write(f"This method achieved the lowest bias score and should be used\n")
    f.write(f"for your final implementation.\n")

print(f"✓ Summary report saved to: {summary_file}")

print("\n" + "=" * 70)
print("COMPARISON COMPLETE!")
print("=" * 70)
print("\nYou now have:")
print("  ✓ Comparison chart showing all methods")
print("  ✓ Summary report ranking the methods")
print("  ✓ Recommendation for best method")

# Show the plot
plt.show()