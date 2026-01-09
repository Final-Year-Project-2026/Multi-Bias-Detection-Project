# 🚀 Multi-Bias Detection System - Quick Start Guide

## Overview

This system now supports **context-aware detection** of **5 types of bias**:
1. **Gender Bias** - Profession-gender associations (not just pronouns!)
2. **Age Bias** - Age-descriptor stereotypes (not just keywords!)
3. **Socioeconomic Bias** - Class-trait associations (not just mentions!)
4. **Regional Bias** - Geographic stereotypes
5. **Sentiment Bias** - Contextual sentiment analysis

⚠️ **Important:** This system uses **CONTEXTUAL ANALYSIS**, not simple word counting!
- It detects "doctor → he" stereotypes, not just pronoun frequency
- It identifies "elderly → slow" associations, not just age keywords
- It analyzes semantic relationships and stereotypical patterns

---

## See the Difference

**Run this demonstration first:**
```bash
python demo_context_aware_detection.py
```

This shows:
- Why "The doctor said he..." is gender bias (profession-gender association)
- Why "The elderly employee was slow..." is age bias (negative stereotype)
- Why simple word counting fails to detect real bias
- How context-aware detection is superior

---

## Quick Start Options

### Option 1: Web Interface (Easiest)

Run the multi-bias web demo:
```bash
streamlit run app_multi_bias.py
```

Features:
- Select which bias types to detect
- Real-time analysis with visual charts
- Interactive bias score displays
- Mitigation suggestions

---

### Option 2: Command Line Analysis

#### Step 1: Generate Text for Specific Bias Type

```bash
# Gender bias
python src/generate_text.py gender

# Age bias
python src/generate_text.py age

# Socioeconomic bias
python src/generate_text.py socioeconomic

# Regional bias
python src/generate_text.py regional

# Sentiment bias
python src/generate_text.py sentiment

# All bias types combined
python src/generate_text.py combined
```

#### Step 2: Analyze the Generated Text

```bash
# Analyze specific bias type
python src/analyze_bias_multi.py gender

# Analyze all bias types
python src/analyze_bias_multi.py combined
```

#### Step 3: Create Bias Table

```bash
python src/create_bias_table_multi.py combined
```

#### Step 4: Visualize Results

```bash
python src/visualize_bias_multi.py combined
```

---

## Understanding the Bias Detector

### Core Module: `bias_detector.py`

The system uses an object-oriented architecture:

```python
from src.bias_detector import MultiBiasDetector

# Detect all bias types
detector = MultiBiasDetector()
results = detector.detect_all(text)

# Detect specific bias types
detector = MultiBiasDetector(['gender', 'age'])
results = detector.detect_all(text)

# Detect single bias type
result = detector.detect_single(text, 'gender')
```

### Bias Score Interpretation

| Score Range | Classification |
|-------------|----------------|
| ±0.5 to ±1.0 | **Strong Bias** 🔴 |
| ±0.3 to ±0.5 | **Moderate Bias** 🟠 |
| ±0.1 to ±0.3 | **Slight Bias** 🔵 |
| -0.1 to +0.1 | **Neutral** 🟢 |

---

## File Structure

### Data Files (Input)
- `data/test_prompts.txt` - Gender bias prompts
- `data/test_prompts_age.txt` - Age bias prompts
- `data/test_prompts_socioeconomic.txt` - Socioeconomic prompts
- `data/test_prompts_regional.txt` - Regional prompts
- `data/test_prompts_sentiment.txt` - Sentiment prompts
- `data/test_prompts_combined.txt` - All types combined

### Result Files (Output)
- `results/generated_outputs_[type].txt` - Generated text
- `results/bias_analysis_[type]_detailed.txt` - Detailed analysis
- `results/bias_summary_[type].txt` - Summary statistics
- `results/bias_table_[type].txt` - Bias comparison table
- `results/bias_visualization_[type].png` - Visual charts

---

## Example Workflows

### Workflow 1: Quick Gender Bias Check

```bash
# 1. Generate
python src/generate_text.py gender

# 2. Analyze
python src/analyze_bias_multi.py gender

# 3. View results
cat results/bias_summary_gender.txt
```

### Workflow 2: Comprehensive Multi-Bias Analysis

```bash
# 1. Generate texts for all bias types
python src/generate_text.py combined

# 2. Analyze all bias types
python src/analyze_bias_multi.py combined

# 3. Create comparison table
python src/create_bias_table_multi.py combined

# 4. Visualize
python src/visualize_bias_multi.py combined
```

### Workflow 3: Web Demo Exploration

```bash
# Launch web interface
streamlit run app_multi_bias.py

# Then:
# 1. Select bias types to detect
# 2. Enter a prompt
# 3. Click "Generate & Analyze"
# 4. Review multi-bias results
```

---

## Testing Individual Bias Detectors

You can test the bias detector module directly:

```bash
python src/bias_detector.py
```

This will run a test with sample text and show detection results for all bias types.

---

## Adding Custom Prompts

Create your own test prompts in the data folder:

```text
# Example: data/my_custom_prompts.txt
The young entrepreneur started
The wealthy investor decided to
The American company announced
```

Then modify `generate_text.py` to use your custom file.

---

## Common Issues & Solutions

### Issue: "Could not find input file"
**Solution**: Run `generate_text.py` first before running analysis scripts.

### Issue: Model loading is slow
**Solution**: First-time model download takes 1-2 minutes. Subsequent runs are faster.

### Issue: Results show no bias
**Solution**: GPT-2 may not always generate biased text. Try different prompts or run multiple times.

### Issue: Import errors
**Solution**: Make sure you're running scripts from the project root directory:
```bash
cd BiasDetectionProject
python src/analyze_bias_multi.py combined
```

---

## Tips for Best Results

1. **Use descriptive prompts** - More specific prompts lead to more detectable bias
2. **Run multiple generations** - AI output varies; multiple runs provide better statistics
3. **Combine bias types** - Use `combined` mode for comprehensive analysis
4. **Check all outputs** - Review both summary and detailed result files
5. **Visualize data** - Charts make bias patterns easier to identify

---

## Next Steps

- Try the web demo: `streamlit run app_multi_bias.py`
- Analyze different bias types independently
- Create custom prompts for your specific use case
- Experiment with mitigation strategies
- Compare results across different bias dimensions

---

## Support

For issues or questions:
1. Check this guide first
2. Review the main README.md
3. Examine the code in `src/bias_detector.py`
4. Check result files for error messages

---

**Happy Bias Detecting! 🔍**
