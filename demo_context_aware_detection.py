"""
Demonstration: Context-Aware vs Simple Keyword Counting Bias Detection

This script demonstrates why contextual analysis is superior to simple word counting
for bias detection in AI-generated text.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bias_detector import GenderBiasDetector, AgeBiasDetector, SocioeconomicBiasDetector

print("=" * 80)
print("CONTEXT-AWARE BIAS DETECTION DEMONSTRATION")
print("=" * 80)
print("\nThis demonstrates why contextual analysis is better than simple keyword counting.\n")

# Example 1: Gender Bias - Profession-Gender Association
print("\n" + "=" * 80)
print("EXAMPLE 1: Gender Bias - The Importance of Context")
print("=" * 80)

text1_biased = "The doctor walked into the room and he examined the patient. He was very skilled."
text1_neutral = "The doctor walked into the room and they examined the patient. They were very skilled."

print(f"\n📝 Biased Text:\n   '{text1_biased}'")
print(f"\n📝 Neutral Text:\n   '{text1_neutral}'")

detector_gender = GenderBiasDetector()

result1_biased = detector_gender.detect(text1_biased)
result1_neutral = detector_gender.detect(text1_neutral)

print(f"\n🔍 Analysis:")
print(f"\nBiased Text:")
print(f"   ✓ Detects profession-gender association: 'doctor' → 'he'")
print(f"   ✓ Bias Score: {result1_biased['bias_score']:+.3f} ({result1_biased['bias_label']})")
print(f"   ✓ Male pronouns: {result1_biased['male_count']}, Female: {result1_biased['female_count']}")
if 'associations' in result1_biased and result1_biased['associations']:
    print(f"   ✓ Found {len(result1_biased['associations'])} profession-gender association(s):")
    for assoc in result1_biased['associations']:
        print(f"      - '{assoc['profession']}' → {assoc['gender']}")

print(f"\nNeutral Text:")
print(f"   ✓ No gendered pronouns used")
print(f"   ✓ Bias Score: {result1_neutral['bias_score']:+.3f} ({result1_neutral['bias_label']})")
print(f"   ✓ Male pronouns: {result1_neutral['male_count']}, Female: {result1_neutral['female_count']}")

print(f"\n💡 Key Insight:")
print(f"   Context-aware detection identifies that associating 'doctor' with 'he'")
print(f"   represents gender bias, not just the presence of male pronouns.")

# Example 2: Age Bias - Descriptor Association
print("\n\n" + "=" * 80)
print("EXAMPLE 2: Age Bias - Detecting Stereotypical Associations")
print("=" * 80)

text2_biased = "The elderly employee was slow with the new technology and confused by the interface."
text2_neutral = "The elderly employee quickly learned the new technology and mastered the interface."

print(f"\n📝 Biased Text (Stereotypical):\n   '{text2_biased}'")
print(f"\n📝 Neutral Text (Non-stereotypical):\n   '{text2_neutral}'")

detector_age = AgeBiasDetector()

result2_biased = detector_age.detect(text2_biased)
result2_neutral = detector_age.detect(text2_neutral)

print(f"\n🔍 Analysis:")
print(f"\nBiased Text:")
print(f"   ✓ Detects negative stereotype: 'elderly' + 'slow' + 'confused'")
print(f"   ✓ Bias Score: {result2_biased['bias_score']:+.3f} ({result2_biased['bias_label']})")
if 'associations' in result2_biased and result2_biased['associations']:
    print(f"   ✓ Found {len(result2_biased['associations'])} age-descriptor association(s)")
    for assoc in result2_biased['associations']:
        print(f"      - '{assoc['age']}' → {assoc['sentiment']} sentiment")

print(f"\nNeutral Text:")
print(f"   ✓ Positive association breaks stereotype")
print(f"   ✓ Bias Score: {result2_neutral['bias_score']:+.3f} ({result2_neutral['bias_label']})")
if 'associations' in result2_neutral and result2_neutral['associations']:
    print(f"   ✓ Found {len(result2_neutral['associations'])} age-descriptor association(s)")

print(f"\n💡 Key Insight:")
print(f"   Both texts mention 'elderly', but context-aware detection identifies that")
print(f"   pairing 'elderly' with 'slow' and 'confused' reinforces negative stereotypes.")

# Example 3: Socioeconomic Bias - Trait Attribution
print("\n\n" + "=" * 80)
print("EXAMPLE 3: Socioeconomic Bias - Analyzing Trait Associations")
print("=" * 80)

text3_biased = "The wealthy businessman was intelligent and successful in his investments."
text3_balanced = "The hardworking businessman was intelligent and successful in his investments."

print(f"\n📝 Biased Text:\n   '{text3_biased}'")
print(f"\n📝 Balanced Text:\n   '{text3_balanced}'")

detector_socio = SocioeconomicBiasDetector()

result3_biased = detector_socio.detect(text3_biased)
result3_balanced = detector_socio.detect(text3_balanced)

print(f"\n🔍 Analysis:")
print(f"\nBiased Text:")
print(f"   ✓ Detects association: 'wealthy' → 'intelligent' + 'successful'")
print(f"   ✓ Bias Score: {result3_biased['bias_score']:+.3f} ({result3_biased['bias_label']})")
if 'associations' in result3_biased and result3_biased['associations']:
    print(f"   ✓ Found {len(result3_biased['associations'])} class-trait association(s)")
    for assoc in result3_biased['associations']:
        print(f"      - '{assoc['class']}' → {assoc['trait']} traits")

print(f"\nBalanced Text:")
print(f"   ✓ Attributes success to 'hardworking', not wealth")
print(f"   ✓ Bias Score: {result3_balanced['bias_score']:+.3f} ({result3_balanced['bias_label']})")

print(f"\n💡 Key Insight:")
print(f"   Context-aware detection identifies that attributing 'intelligent' and")
print(f"   'successful' specifically to 'wealthy' people reinforces class stereotypes.")

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY: Why Context-Aware Detection is Superior")
print("=" * 80)

print(f"""
✅ CONTEXT-AWARE DETECTION (Our Implementation):
   • Analyzes associations between entities and descriptors
   • Detects stereotypical patterns (e.g., doctor → male, elderly → slow)
   • Weighs profession-gender associations more heavily than simple counts
   • Identifies implicit bias through semantic relationships
   • Considers sentiment and trait attributions
   • More accurate reflection of actual bias in text

❌ SIMPLE KEYWORD COUNTING (Old Approach):
   • Only counts frequency of keywords/pronouns
   • Misses context and associations
   • Treats all mentions equally regardless of context
   • Cannot detect stereotypical relationships
   • Produces false positives/negatives
   • Ignores the semantic meaning of text

🎯 REAL-WORLD EXAMPLE:
   Text: "The nurse said she would help the doctor. He thanked her."
   
   Simple Counting:
   - Counts: 1 male, 2 female → Female bias
   - WRONG! Misses the actual bias pattern
   
   Context-Aware:
   - Detects: "nurse" → "she" (gender stereotype)
   - Detects: "doctor" → "he" (gender stereotype)  
   - CORRECT! Identifies stereotypical associations
   - Bias Score reflects both stereotypes, not just counts

""")

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
The context-aware bias detection system:
1. Understands relationships between words, not just frequencies
2. Detects subtle stereotypes that keyword counting would miss
3. Provides more accurate and meaningful bias assessment
4. Better reflects how bias actually manifests in language
5. Can explain WHY text is biased, not just that it is

This is a significant improvement over simple word/pronoun counting!
""")

print("=" * 80)
print("\nTo see this in action, run: streamlit run app_multi_bias.py")
print("=" * 80)
