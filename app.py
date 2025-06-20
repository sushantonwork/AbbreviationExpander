import streamlit as st
import json
import html
from expander import load_abbreviation_dict, expand_abbreviations

st.set_page_config(page_title="Abbreviation Expander", layout="wide")

# Enhanced Custom CSS with fixed overflow handling
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
            padding: 0.5rem; /* Decreased from 1rem */
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3);
        }

        .main-title {
            font-size: 1.4rem; /* Decreased from 2rem */
            font-weight: 600;  /* Slightly lighter */
            color: white;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.75rem; /* Decreased from 0.9rem */
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
            caret-color: #1e293b !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #1e3a8a !important;
            box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.2) !important;
            outline: none !important;
        }
        
        /* Output Container - FIXED OVERFLOW */
        .output-container {
            background: #ffffff;
            border: 1px solid #3730a3;
            border-top: none;
            border-radius: 0 0 6px 6px;
            height: 420px;
            overflow-y: auto !important;  /* Changed from auto to auto !important */
            overflow-x: hidden !important; /* Hide horizontal overflow */
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
            word-wrap: break-word !important; /* Break long words */
            white-space: pre-wrap !important;  /* Preserve whitespace but wrap */
        }
        
        /* Scrollbar Styling */
        .output-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .output-container::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 4px;
        }
        
        .output-container::-webkit-scrollbar-thumb {
            background: #3730a3;
            border-radius: 4px;
        }
        
        .output-container::-webkit-scrollbar-thumb:hover {
            background: #1e3a8a;
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
            display: inline-block; /* Ensure marks don't break layout */
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
        section[data-testid="stSidebar"] {
            background: #f8fafc !important;
            border-right: 1px solid #3730a3 !important;
            padding: 1rem !important;
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
        <h1 class='main-title'>NEMO</h1>
        <p class='subtitle'>Transform abbreviated text into fully expanded, professional content</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:

    # Use st.image directly - more reliable in cloud
    try:
        st.image("logo.png", width=250)
    except Exception as e:
        # Fallback if image fails
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; margin: 1rem 0;
                    background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%); 
                    border-radius: 12px; color: white;">
            <h2 style="margin: 0; font-size: 2rem; font-weight: bold;">🔄 NEMO</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                Text Expansion Tool
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin: 0 0 1rem 0; color: #1e293b; font-size: 1.2rem;'>File Upload</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 1rem;'>Upload your custom abbreviation dictionary</p>", unsafe_allow_html=True)
    
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
    abbr_dict = load_abbreviation_dict("abbreviations4.xlsx")

# Main Content Area
col1, col2 = st.columns(2, gap="large")

# Left Column: Original Text Input
with col1:
    st.markdown("""
        <div class='section-header'>
            📝 Original Text
        </div>
    """, unsafe_allow_html=True)
    
    original_text = st.text_area("", height=420, key="input_text", label_visibility="collapsed")
    
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
    
    # Escape HTML content to prevent injection, but preserve our mark tags
    if "highlighted" in st.session_state and st.session_state["highlighted"]:
        # First escape all HTML
        safe_highlighted = html.escape(st.session_state["highlighted"])
        # Then restore our mark tags
        safe_highlighted = safe_highlighted.replace("&lt;mark&gt;", "<mark>")
        safe_highlighted = safe_highlighted.replace("&lt;/mark&gt;", "</mark>")
        # Preserve line breaks
        safe_highlighted = safe_highlighted.replace("\n", "<br>")
    else:
        safe_highlighted = highlighted
    
    st.markdown(f"""
        <div class='output-container'>
            {safe_highlighted}
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
            # Store the plain text version (without HTML tags)
            st.session_state["expanded"] = expanded_text
            st.session_state["highlighted"] = highlighted_text
        st.rerun()

if "expanded" in st.session_state:
    with btn_col2:
        # Create a download button for the expanded text
        st.download_button(
            label="⬇️ Download",
            data=st.session_state["expanded"],
            file_name="expanded_text.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with btn_col3:
        # JavaScript copy functionality with proper escaping
        import json
        # Properly escape the text for JavaScript
        escaped_text = json.dumps(st.session_state["expanded"])[1:-1]  # Remove quotes added by json.dumps
        
        copy_js = f"""
        <script>
        function copyToClipboard() {{
            const text = "{escaped_text}";
            navigator.clipboard.writeText(text).then(function() {{
                const btn = document.getElementById("copyBtn");
                btn.innerText = "✅ Copied!";
                btn.style.background = "linear-gradient(135deg, #15803d, #16a34a)";
                setTimeout(() => {{
                    btn.innerText = "📋 Copy to Clipboard";
                    btn.style.background = "linear-gradient(135deg, #1e3a8a, #1e40af)";
                }}, 2000);
            }}, function(err) {{
                alert("Failed to copy text. Please try again.");
            }});
        }}
        </script>
        <button id="copyBtn" onclick="copyToClipboard()" 
            style="background: linear-gradient(135deg, #1e3a8a, #1e40af); color: white; border: none; border-radius: 6px; padding: 0.6rem 1.2rem; font-weight: 600; font-size: 13px; width: 100%; cursor: pointer; transition: all 0.3s ease;">
            📋 Copy to Clipboard
        </button>
        """
        st.components.v1.html(copy_js, height=50)

# Footer
st.markdown("""
<hr style='margin: 1rem 0 0.5rem 0; border: none; height: 1px; background: #e2e8f0;'>
<div style='text-align: center; color: #64748b; font-size: 12px; padding-bottom: 0.5rem;'>
    Built with ❤️ using Streamlit • Transform your abbreviated text efficiently
</div>
""", unsafe_allow_html=True)