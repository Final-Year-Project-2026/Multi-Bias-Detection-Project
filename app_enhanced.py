import streamlit as st
from transformers import pipeline
import re
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Gender Bias Detection & Mitigation",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🔍 Gender Bias Detection & Mitigation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Demo with Multiple Mitigation Strategies</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mitigation_method = st.selectbox(
        "Choose Mitigation Method:",
        ["Replace with They/Them", "Remove Pronouns", "Prompt Engineering"]
    )
    
    show_advanced = st.checkbox("Show Advanced Analysis", value=False)
    
    st.markdown("---")
    
    st.header("ℹ️ About")
    st.write("""
    This system demonstrates:
    - Real-time bias detection
    - Multiple mitigation strategies
    - Visual bias analysis
    - Comparative metrics
    """)
    
    st.header("📊 Bias Scale")
    st.write("""
    - **+1.0** to **+0.5**: Strong male bias
    - **+0.5** to **+0.1**: Moderate male bias
    - **+0.1** to **-0.1**: Neutral
    - **-0.1** to **-0.5**: Moderate female bias
    - **-0.5** to **-1.0**: Strong female bias
    """)

# Load model
@st.cache_resource
def load_model():
    return pipeline('text-generation', model='gpt2')

# Functions
MALE_PRONOUNS = ['he', 'him', 'his', 'himself']
FEMALE_PRONOUNS = ['she', 'her', 'hers', 'herself']

def count_pronouns(text):
    text_lower = text.lower()
    male_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) for p in MALE_PRONOUNS)
    female_count = sum(len(re.findall(r'\b' + p + r'\b', text_lower)) for p in FEMALE_PRONOUNS)
    return male_count, female_count

def calculate_bias_score(male_count, female_count):
    total = male_count + female_count
    return (male_count - female_count) / total if total > 0 else 0.0

def get_bias_label(bias_score):
    if bias_score > 0.5:
        return "STRONG MALE BIAS", "#2196F3"
    elif bias_score > 0.1:
        return "Moderate Male Bias", "#64B5F6"
    elif bias_score < -0.5:
        return "STRONG FEMALE BIAS", "#E91E63"
    elif bias_score < -0.1:
        return "Moderate Female Bias", "#F06292"
    else:
        return "Neutral/Balanced", "#4CAF50"

def debias_replace_they(text):
    text = re.sub(r'\bhe\b', 'they', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'they', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhim\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhis\b', 'their', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhers\b', 'theirs', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhimself\b', 'themselves', text, flags=re.IGNORECASE)
    text = re.sub(r'\bherself\b', 'themselves', text, flags=re.IGNORECASE)
    return text

def debias_remove_pronouns(text):
    text = re.sub(r'\bhe\b', 'the person', text, flags=re.IGNORECASE)
    text = re.sub(r'\bshe\b', 'the person', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhim\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bher\b', 'them', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhis\b', 'their', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhers\b', 'theirs', text, flags=re.IGNORECASE)
    return text

def create_bias_gauge(bias_score):
    """Create a gauge chart for bias score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=bias_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Bias Score"},
        delta={'reference': 0},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.5], 'color': "#FCE4EC"},
                {'range': [-0.5, -0.1], 'color': "#F8BBD0"},
                {'range': [-0.1, 0.1], 'color': "#C8E6C9"},
                {'range': [0.1, 0.5], 'color': "#BBDEFB"},
                {'range': [0.5, 1], 'color': "#E3F2FD"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': bias_score
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# Main interface
st.markdown("---")

# Input
col1, col2 = st.columns([3, 1])

with col1:
    user_prompt = st.text_input(
        "Enter your prompt:",
        value="The doctor walked into the room and",
        help="Enter an incomplete sentence"
    )

with col2:
    st.write("")
    st.write("")
    generate_button = st.button("🚀 Generate & Analyze", type="primary", use_container_width=True)

# Quick examples
st.markdown("**💡 Quick Examples:**")
ex1, ex2, ex3, ex4 = st.columns(4)

with ex1:
    if st.button("👨‍⚕️ Doctor"):
        user_prompt = "The doctor walked into the room and"
        generate_button = True

with ex2:
    if st.button("👩‍⚕️ Nurse"):
        user_prompt = "The nurse prepared the medication and"
        generate_button = True

with ex3:
    if st.button("👨‍💼 CEO"):
        user_prompt = "The CEO announced the new policy and"
        generate_button = True

with ex4:
    if st.button("👨‍🔧 Engineer"):
        user_prompt = "The engineer solved the problem by"
        generate_button = True

st.markdown("---")

# Generation
if generate_button and user_prompt:
    with st.spinner("🤖 Initializing AI model..."):
        generator = load_model()
    
    with st.spinner("✨ Generating and analyzing..."):
        # Generate
        output = generator(user_prompt, max_length=50, num_return_sequences=1, 
                          temperature=0.7, do_sample=True)
        original_text = output[0]['generated_text']
        
        # Analyze original
        male_count, female_count = count_pronouns(original_text)
        bias_score = calculate_bias_score(male_count, female_count)
        bias_label, bias_color = get_bias_label(bias_score)
        
        # Apply mitigation
        if mitigation_method == "Replace with They/Them":
            debiased_text = debias_replace_they(original_text)
        elif mitigation_method == "Remove Pronouns":
            debiased_text = debias_remove_pronouns(original_text)
        else:  # Prompt Engineering
            debiased_prompt = f"{user_prompt} [Respond without gender assumptions]"
            output_deb = generator(debiased_prompt, max_length=50, num_return_sequences=1,
                                 temperature=0.7, do_sample=True)
            debiased_text = output_deb[0]['generated_text']
        
        # Analyze debiased
        male_deb, female_deb = count_pronouns(debiased_text)
        bias_deb = calculate_bias_score(male_deb, female_deb)
        label_deb, color_deb = get_bias_label(bias_deb)
        
    st.success("✅ Analysis Complete!")
    
    # Results
    col_orig, col_mit = st.columns(2)
    
    with col_orig:
        st.markdown("### 📝 Original Text")
        st.info(original_text)
        
        st.markdown("#### Analysis")
        metric1, metric2 = st.columns(2)
        with metric1:
            st.metric("Male Pronouns", male_count)
        with metric2:
            st.metric("Female Pronouns", female_count)
        
        st.plotly_chart(create_bias_gauge(bias_score), use_container_width=True)
        
        st.markdown(f"**Classification:** :{bias_color}[{bias_label}]")
    
    with col_mit:
        st.markdown(f"### ✨ Mitigated Text")
        st.markdown(f"*Method: {mitigation_method}*")
        st.success(debiased_text)
        
        st.markdown("#### Analysis")
        metric1, metric2 = st.columns(2)
        with metric1:
            st.metric("Male Pronouns", male_deb, delta=male_deb - male_count, delta_color="inverse")
        with metric2:
            st.metric("Female Pronouns", female_deb, delta=female_deb - female_count, delta_color="inverse")
        
        st.plotly_chart(create_bias_gauge(bias_deb), use_container_width=True)
        
        st.markdown(f"**Classification:** :{color_deb}[{label_deb}]")
        
        # Improvement
        improvement = abs(bias_score) - abs(bias_deb)
        if improvement > 0:
            st.success(f"✅ Bias reduced by {improvement:.3f} ({improvement/abs(bias_score)*100:.1f}%)")
    
    # Advanced analysis
    if show_advanced:
        st.markdown("---")
        st.markdown("### 🔬 Advanced Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Detailed Metrics", "Comparison Chart", "Statistical Info"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Text Metrics:**")
                st.json({
                    "Total Pronouns": male_count + female_count,
                    "Male Pronouns": male_count,
                    "Female Pronouns": female_count,
                    "Bias Score": round(bias_score, 3),
                    "Classification": bias_label
                })
            
            with col2:
                st.markdown("**Mitigated Text Metrics:**")
                st.json({
                    "Total Pronouns": male_deb + female_deb,
                    "Male Pronouns": male_deb,
                    "Female Pronouns": female_deb,
                    "Bias Score": round(bias_deb, 3),
                    "Classification": label_deb
                })
        
        with tab2:
            # Create comparison chart
            fig = go.Figure(data=[
                go.Bar(name='Male', x=['Original', 'Mitigated'], y=[male_count, male_deb], marker_color='#2196F3'),
                go.Bar(name='Female', x=['Original', 'Mitigated'], y=[female_count, female_deb], marker_color='#E91E63')
            ])
            fig.update_layout(barmode='group', title='Pronoun Count Comparison', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("**Statistical Summary:**")
            st.write(f"- Mitigation Method Used: {mitigation_method}")
            st.write(f"- Original Bias: {bias_score:+.3f}")
            st.write(f"- Mitigated Bias: {bias_deb:+.3f}")
            st.write(f"- Absolute Bias Reduction: {abs(bias_score) - abs(bias_deb):.3f}")
            st.write(f"- Pronoun Reduction: {(male_count + female_count) - (male_deb + female_deb)} total")
    
    # Export
    st.markdown("---")
    export_text = f"""BIAS ANALYSIS REPORT
{'='*60}

PROMPT: {user_prompt}

ORIGINAL TEXT: {original_text}
- Male pronouns: {male_count}
- Female pronouns: {female_count}
- Bias score: {bias_score:+.3f}
- Classification: {bias_label}

MITIGATED TEXT ({mitigation_method}): {debiased_text}
- Male pronouns: {male_deb}
- Female pronouns: {female_deb}
- Bias score: {bias_deb:+.3f}
- Classification: {label_deb}

IMPROVEMENT: {improvement:.3f} ({improvement/abs(bias_score)*100:.1f}% reduction)
"""
    
    st.download_button("📥 Download Report", export_text, file_name="bias_report.txt")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built with ❤️ for MCA Final Year Project</div>", unsafe_allow_html=True)