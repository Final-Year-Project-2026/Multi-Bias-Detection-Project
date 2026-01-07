import streamlit as st
from transformers import pipeline
import re
import time

# Page configuration
st.set_page_config(
    page_title="Gender Bias Detection & Mitigation",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F77B4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bias-metric {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .male-bias {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .female-bias {
        background-color: #FCE4EC;
        border-left: 4px solid #E91E63;
    }
    .neutral {
        background-color: #F1F8E9;
        border-left: 4px solid #8BC34A;
    }
    .stProgress > div > div > div > div {
        background-color: #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🔍 Gender Bias Detection & Mitigation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">MCA Final Year Project - AI Language Model Bias Analysis</div>', unsafe_allow_html=True)

# Sidebar - Information
with st.sidebar:
    st.header("ℹ️ About This Project")
    st.write("""
    This system detects and mitigates gender bias in AI-generated text.
    
    **How it works:**
    1. Enter a prompt
    2. AI generates text
    3. System analyzes bias
    4. Shows debiased versions
    
    **Bias Detection:**
    - Counts male vs female pronouns
    - Calculates bias score (-1 to +1)
    - Highlights biased language
    """)
    
    st.header("📊 Bias Score Guide")
    st.write("""
    - **+1.0**: Strong male bias
    - **+0.5**: Moderate male bias
    - **0.0**: Neutral (balanced)
    - **-0.5**: Moderate female bias
    - **-1.0**: Strong female bias
    """)
    
    st.header("👨‍💻 Developer Info")
    st.write("MCA Final Year Project")
    st.write("Bias Detection in LLM-Generated Content")

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'results' not in st.session_state:
    st.session_state.results = {}

# Load model (cached)
@st.cache_resource
def load_model():
    return pipeline('text-generation', model='gpt2')

# Pronoun counting functions
MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']

def count_pronouns(text):
    """Count male and female pronouns in text"""
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
    """Calculate bias score"""
    total = male_count + female_count
    if total == 0:
        return 0.0
    return (male_count - female_count) / total

def get_bias_label(bias_score):
    """Get human-readable bias label"""
    if bias_score > 0.5:
        return "STRONG MALE BIAS", "male-bias"
    elif bias_score > 0.1:
        return "Moderate Male Bias", "male-bias"
    elif bias_score < -0.5:
        return "STRONG FEMALE BIAS", "female-bias"
    elif bias_score < -0.1:
        return "Moderate Female Bias", "female-bias"
    else:
        return "Neutral/Balanced", "neutral"

def highlight_pronouns(text):
    """Highlight gendered pronouns in text"""
    highlighted = text
    
    # Highlight male pronouns in blue
    for pronoun in MALE_PRONOUNS:
        pattern = r'\b(' + pronoun + r')\b'
        highlighted = re.sub(pattern, r'**[\1]**', highlighted, flags=re.IGNORECASE)
    
    # Highlight female pronouns in pink
    for pronoun in FEMALE_PRONOUNS:
        pattern = r'\b(' + pronoun + r')\b'
        highlighted = re.sub(pattern, r'***[\1]***', highlighted, flags=re.IGNORECASE)
    
    return highlighted

# Debiasing functions
def debias_replace_they(text):
    """Replace gendered pronouns with they/them"""
    text = re.sub(r'\bhe\b', 'they', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'they', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhim\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhis\b', 'their', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhers\b', 'theirs', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhimself\b', 'themselves', text, flags=re.IGNORECASE)
    text = re.sub(r'\bherself\b', 'themselves', text, flags=re.IGNORECASE)
    return text

def debias_prompt_engineering(prompt, generator):
    """Generate with debiasing instruction"""
    debiased_prompt = f"{prompt} [Respond without gender assumptions or stereotypes]"
    output = generator(debiased_prompt, max_length=50, num_return_sequences=1, 
                      temperature=0.7, do_sample=True)
    return output[0]['generated_text']

# Main interface
st.markdown("---")

# Input section
col1, col2 = st.columns([3, 1])

with col1:
    user_prompt = st.text_input(
        "Enter your prompt:",
        value="The doctor walked into the room and",
        help="Enter an incomplete sentence. The AI will complete it."
    )

with col2:
    st.write("")
    st.write("")
    generate_button = st.button("🚀 Generate & Analyze", type="primary", use_container_width=True)

# Example prompts
st.markdown("**💡 Example prompts:**")
examples_col1, examples_col2, examples_col3 = st.columns(3)

with examples_col1:
    if st.button("👨‍⚕️ The nurse prepared..."):
        st.session_state.example_prompt = "The nurse prepared the medication and"
        st.rerun()

with examples_col2:
    if st.button("👨‍💼 The CEO announced..."):
        st.session_state.example_prompt = "The CEO announced the new policy and"
        st.rerun()

with examples_col3:
    if st.button("👨‍🔧 The engineer solved..."):
        st.session_state.example_prompt = "The engineer solved the problem by"
        st.rerun()

# Handle example prompts
if 'example_prompt' in st.session_state:
    user_prompt = st.session_state.example_prompt
    del st.session_state.example_prompt
    st.rerun()

st.markdown("---")

# Generation and analysis
if generate_button and user_prompt:
    with st.spinner("🤖 Loading AI model..."):
        generator = load_model()
    
    with st.spinner("✨ Generating text..."):
        # Generate original text
        output = generator(user_prompt, max_length=50, num_return_sequences=1, 
                          temperature=0.7, do_sample=True)
        original_text = output[0]['generated_text']
        
        # Count pronouns and calculate bias
        male_count, female_count = count_pronouns(original_text)
        bias_score = calculate_bias_score(male_count, female_count)
        bias_label, bias_class = get_bias_label(bias_score)
        
        # Generate debiased versions
        debiased_post = debias_replace_they(original_text)
        male_post, female_post = count_pronouns(debiased_post)
        bias_post = calculate_bias_score(male_post, female_post)
        label_post, class_post = get_bias_label(bias_post)
        
        # Store results
        st.session_state.results = {
            'original_text': original_text,
            'male_count': male_count,
            'female_count': female_count,
            'bias_score': bias_score,
            'bias_label': bias_label,
            'bias_class': bias_class,
            'debiased_post': debiased_post,
            'male_post': male_post,
            'female_post': female_post,
            'bias_post': bias_post,
            'label_post': label_post,
            'class_post': class_post
        }
        
        st.session_state.generated = True

# Display results
if st.session_state.generated:
    results = st.session_state.results
    
    st.success("✅ Analysis Complete!")
    
    # Main results in two columns
    col_original, col_mitigated = st.columns(2)
    
    with col_original:
        st.markdown("### 📝 Original Generated Text")
        
        # Display text with highlighted pronouns
        st.markdown(f"**Generated:** {results['original_text']}")
        st.markdown("")
        st.markdown(f"**With Highlights:** {highlight_pronouns(results['original_text'])}")
        st.caption("Blue [brackets] = male pronouns, Pink ***brackets*** = female pronouns")
        
        # Pronoun counts
        st.markdown("#### 📊 Pronoun Analysis")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Male Pronouns", results['male_count'], delta=None)
        with metric_col2:
            st.metric("Female Pronouns", results['female_count'], delta=None)
        
        # Bias score
        st.markdown("#### 🎯 Bias Score")
        
        # Progress bar for bias score
        bias_normalized = (results['bias_score'] + 1) / 2  # Convert -1 to 1 range to 0 to 1
        st.progress(bias_normalized)
        
        st.markdown(f"**Score:** {results['bias_score']:+.3f}")
        st.markdown(f"**Classification:** {results['bias_label']}")
        
        # Colored box based on bias
        if results['bias_score'] > 0.1:
            st.info("⚠️ This text shows **male bias** (uses more male pronouns)")
        elif results['bias_score'] < -0.1:
            st.info("⚠️ This text shows **female bias** (uses more female pronouns)")
        else:
            st.success("✅ This text is relatively **neutral** (balanced pronouns)")
    
    with col_mitigated:
        st.markdown("### ✨ Mitigated (Debiased) Text")
        
        # Display debiased text
        st.markdown(f"**Debiased:** {results['debiased_post']}")
        st.caption("Method: Replace with they/them pronouns")
        
        # Pronoun counts
        st.markdown("#### 📊 Pronoun Analysis")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Male Pronouns", results['male_post'], 
                     delta=results['male_post'] - results['male_count'],
                     delta_color="inverse")
        with metric_col2:
            st.metric("Female Pronouns", results['female_post'], 
                     delta=results['female_post'] - results['female_count'],
                     delta_color="inverse")
        
        # Bias score
        st.markdown("#### 🎯 Bias Score")
        
        # Progress bar for bias score
        bias_normalized_post = (results['bias_post'] + 1) / 2
        st.progress(bias_normalized_post)
        
        st.markdown(f"**Score:** {results['bias_post']:+.3f}")
        st.markdown(f"**Classification:** {results['label_post']}")
        
        # Improvement indicator
        bias_reduction = abs(results['bias_score']) - abs(results['bias_post'])
        if bias_reduction > 0:
            st.success(f"✅ **Bias reduced by {bias_reduction:.3f}** ({(bias_reduction/abs(results['bias_score'])*100):.1f}%)")
        elif bias_reduction == 0:
            st.info("→ Bias already eliminated!")
        else:
            st.warning("⚠️ Bias increased (this shouldn't happen with this method)")
    
    # Comparison section
    st.markdown("---")
    st.markdown("### 📊 Side-by-Side Comparison")
    
    comparison_data = {
        'Metric': ['Male Pronouns', 'Female Pronouns', 'Bias Score', 'Classification'],
        'Original': [
            results['male_count'],
            results['female_count'],
            f"{results['bias_score']:+.3f}",
            results['bias_label']
        ],
        'Mitigated': [
            results['male_post'],
            results['female_post'],
            f"{results['bias_post']:+.3f}",
            results['label_post']
        ]
    }
    
    st.table(comparison_data)
    
    # Download results
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    export_text = f"""BIAS DETECTION & MITIGATION RESULTS
{'='*60}

INPUT PROMPT:
{user_prompt}

ORIGINAL TEXT:
{results['original_text']}

ORIGINAL ANALYSIS:
- Male pronouns: {results['male_count']}
- Female pronouns: {results['female_count']}
- Bias score: {results['bias_score']:+.3f}
- Classification: {results['bias_label']}

MITIGATED TEXT:
{results['debiased_post']}

MITIGATED ANALYSIS:
- Male pronouns: {results['male_post']}
- Female pronouns: {results['female_post']}
- Bias score: {results['bias_post']:+.3f}
- Classification: {results['label_post']}

IMPROVEMENT:
- Bias reduction: {abs(results['bias_score']) - abs(results['bias_post']):.3f}
"""
    
    st.download_button(
        label="📥 Download Results as Text",
        data=export_text,
        file_name="bias_analysis_results.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎓 <strong>MCA Final Year Project</strong> | Bias Detection and Mitigation in LLM-Generated Content</p>
    <p>Built with Streamlit 🎈 and Hugging Face Transformers 🤗</p>
</div>
""", unsafe_allow_html=True)