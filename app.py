import streamlit as st
from expander import load_abbreviation_dict, expand_abbreviations

st.set_page_config(page_title="Abbreviation Expander", layout="wide")

# Enhanced Custom CSS inspired by DiffChecker
st.markdown("""
    <style>
        /* Global Styles */
        .main {
            padding-top: 0.5rem;
            max-height: 100vh;
            overflow: hidden;
        }
        
        /* Header Styles */
        .header-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3);
        }
        
        .main-title {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.9rem;
            margin-top: 0.25rem;
            font-weight: 300;
        }
        
        /* Section Headers */
        .section-header {
            background: #1e3a8a;
            border: 1px solid #3730a3;
            border-radius: 6px 6px 0 0;
            padding: 0.75rem 1rem;
            margin: 0;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Text Areas */
        /* Text Area Fix with Caret */
        .stTextArea > div > div > textarea {
            background-color: #ffffff !important;
            border: 1px solid #3730a3 !important;
            border-top: none !important;
            border-radius: 0 0 6px 6px !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            color: #1e293b !important;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
            resize: none !important;
            padding: 1rem !important;
            caret-color: #1e293b !important; /* <-- ensures cursor is visible */
        }

        
        .stTextArea > div > div > textarea:focus {
            border-color: #1e3a8a !important;
            box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.2) !important;
            outline: none !important;
        }
        
        /* Output Container */
        .output-container {
            background: #ffffff;
            border: 1px solid #3730a3;
            border-top: none;
            border-radius: 0 0 6px 6px;
            height: 280px;
            overflow-y: auto;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
        }
        
        .output-placeholder {
            color: #64748b;
            font-style: italic;
            text-align: center;
            margin-top: 5rem;
        }
        
        /* Highlighting */
        mark {
            background: linear-gradient(135deg, #fef3c7, #fde68a);
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 500;
            border: 1px solid #f59e0b;
        }
        
        /* Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 6px rgba(220, 38, 38, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Copy Button Special Style */
        .copy-button button {
            background: linear-gradient(135deg, #1e3a8a, #1e40af) !important;
            box-shadow: 0 3px 6px rgba(30, 58, 138, 0.3) !important;
        }
        
        .copy-button button:hover {
            box-shadow: 0 6px 12px rgba(30, 58, 138, 0.4) !important;
        }
        
        /* Sidebar Styles */
        .css-1d391kg {
            background: #f8fafc;
            border-right: 1px solid #3730a3;
        }
        
        .sidebar-section {
            background: white;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(30, 58, 138, 0.1);
            border: 1px solid #e2e8f0;
        }
        
        /* Stats Bar */
        .stats-bar {
            background: #f1f5f9;
            border: 1px solid #3730a3;
            border-top: none;
            border-radius: 0 0 6px 6px;
            padding: 0.5rem 1rem;
            font-size: 11px;
            color: #64748b;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        /* Success/Warning Messages */
        .stSuccess {
            background: #f0fdf4 !important;
            border: 1px solid #bbf7d0 !important;
            border-radius: 6px !important;
            color: #15803d !important;
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stWarning {
            background: #fffbeb !important;
            border: 1px solid #fed7aa !important;
            border-radius: 6px !important;
            color: #d97706 !important;
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Container Height Control */
        .block-container {
            max-height: 100vh !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Compact spacing */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class='header-container'>
        <h1 class='main-title'>Abbreviation Expander</h1>
        <p class='subtitle'>Transform abbreviated text into fully expanded, professional content</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div class='sidebar-section'>
            <h3 style='margin: 0 0 1rem 0; color: #1e293b; font-size: 1.2rem;'>📁 File Upload</h3>
            <p style='color: #64748b; font-size: 14px; margin-bottom: 1rem;'>Upload your custom abbreviation dictionary</p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose Excel file (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        st.markdown("""
            <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 0.75rem; margin-top: 1rem;'>
                <span style='color: #15803d; font-size: 14px;'>✅ Custom dictionary loaded</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background: #fef3c7; border: 1px solid #fde68a; border-radius: 6px; padding: 0.75rem; margin-top: 1rem;'>
                <span style='color: #d97706; font-size: 14px;'>ℹ️ Using default dictionary</span>
            </div>
        """, unsafe_allow_html=True)

# Load abbreviation dictionary
if uploaded_file:
    abbr_dict = load_abbreviation_dict(uploaded_file)
else:
    abbr_dict = load_abbreviation_dict("abbreviations3.xlsx")

# Main Content Area
col1, col2 = st.columns(2, gap="large")

# Left Column: Original Text Input
with col1:
    st.markdown("""
        <div class='section-header'>
            📝 Original Text
        </div>
    """, unsafe_allow_html=True)
    
    original_text = st.text_area("", height=280, key="input_text", label_visibility="collapsed")
    
    # Stats for original text
    char_count = len(original_text) if original_text else 0
    word_count = len(original_text.split()) if original_text and original_text.strip() else 0
    
    st.markdown(f"""
        <div class='stats-bar'>
            <div class='stat-item'>📊 Characters: {char_count}</div>
            <div class='stat-item'>📝 Words: {word_count}</div>
        </div>
    """, unsafe_allow_html=True)

# Right Column: Expanded Text Output
with col2:
    st.markdown("""
        <div class='section-header'>
            🚀 Expanded Text
        </div>
    """, unsafe_allow_html=True)
    
    # Output container
    if "highlighted" in st.session_state:
        highlighted = st.session_state["highlighted"]
        expanded_char_count = len(st.session_state.get("expanded", ""))
        expanded_word_count = len(st.session_state.get("expanded", "").split()) if st.session_state.get("expanded") else 0
    else:
        highlighted = "<div class='output-placeholder'>Expanded text will appear here...</div>"
        expanded_char_count = 0
        expanded_word_count = 0
    
    st.markdown(f"""
        <div class='output-container'>
            {highlighted}
        </div>
    """, unsafe_allow_html=True)
    
    # Stats for expanded text
    st.markdown(f"""
        <div class='stats-bar'>
            <div class='stat-item'>📊 Characters: {expanded_char_count}</div>
            <div class='stat-item'>📝 Words: {expanded_word_count}</div>
        </div>
    """, unsafe_allow_html=True)

# Action Buttons
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

with btn_col1:
    expand_clicked = st.button("🔄 Expand Text", use_container_width=True)


# Handle button clicks
if expand_clicked:
    if not original_text.strip():
        st.warning("⚠️ Please enter some text to expand.")
    else:
        with st.spinner("Expanding abbreviations..."):
            expanded_text, highlighted_text = expand_abbreviations(original_text, abbr_dict)
            st.session_state["expanded"] = expanded_text
            st.session_state["highlighted"] = highlighted_text
        st.rerun()

if "expanded" in st.session_state:
    copy_js = f"""
    <script>
    function copyToClipboard(text) {{
        navigator.clipboard.writeText(text).then(function() {{
            const msg = document.getElementById("copy-status");
            msg.innerText = "✅ Text copied to clipboard!";
            msg.style.color = "green";
        }}, function(err) {{
            const msg = document.getElementById("copy-status");
            msg.innerText = "❌ Failed to copy text.";
            msg.style.color = "red";
        }});
    }}
    </script>
    <button onclick="copyToClipboard(`{st.session_state["expanded"].replace("`", "\\`")}`)" 
        style="background: linear-gradient(135deg, #1e3a8a, #1e40af); color: white; border: none; border-radius: 6px; padding: 0.6rem 1.2rem; font-weight: 600; font-size: 13px;">
        📋 Copy Result
    </button>
    <p id="copy-status" style="font-size: 13px; margin-top: 5px;"></p>
    """
    st.components.v1.html(copy_js, height=100)


# Footer
st.markdown("""
<hr style='margin: 1rem 0 0.5rem 0; border: none; height: 1px; background: #e2e8f0;'>
<div style='text-align: center; color: #64748b; font-size: 12px; padding-bottom: 0.5rem;'>
    Built with ❤️ using Streamlit • Transform your abbreviated text efficiently
</div>
""", unsafe_allow_html=True)