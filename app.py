import streamlit as st
import json
import html
from expander import load_abbreviation_dict, expand_abbreviations
import base64

st.set_page_config(page_title="Abbreviation Expander", layout="wide")

# Function to encode image to base64
def get_base64_of_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

uploaded_file = st.sidebar.file_uploader("Choose Excel file (.xlsx)", type=["xlsx"])
# Sidebar
with st.sidebar:
    st.markdown("<h3 style='margin: 0 0 1rem 0; color: #1e293b; font-size: 1.2rem;'>File Upload</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 1rem;'>Upload your custom abbreviation dictionary</p>", unsafe_allow_html=True)
    
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

# Enhanced Custom CSS with logo support
st.markdown("""
    <style>
        /* Global Styles */
        .main {
            padding-top: 3rem !important;
            overflow: visible !important;  /* allow visible overflow */
        }       

        /* Container Height Control */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
            overflow: visible !important;  /* allow visible overflow */
            max-width: none !important;
        }
        
        /* Header Styles with Logo */
        .header-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3);
            display: flex;
            align-items: center;
            position: relative;
        }



        .logo-container {
            background: white;
            padding: 0.5rem;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            height: 60px;
            min-width: 120px;
        }

        .logo-container img {
            max-height: 50px;
            max-width: 100%;
            object-fit: contain;
        }

        .header-content {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
        }

        .main-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: white !important;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            margin-bottom: 1.80rem;  /* ✅ Add this line */
            font-weight: 300;
        }

        /* Column Layout Fixes */
        .stColumn {
            padding: 0 0.5rem !important;
            display: flex;
            flex-direction: column;
        }
        
        .stColumn:first-child {
            padding-left: 0 !important;
        }
        
        .stColumn:last-child {
            padding-right: 0 !important;
        }
        
        /* Ensure consistent column content alignment */
        .stColumn > div {
            display: flex;
            flex-direction: column;
        }
        
        /* Section Headers */
        .section-header {
            background: #1e3a8a;
            border: 1px solid #3730a3;
            border-radius: 6px 6px 0 0;
            padding: 0.75rem 1rem;
            margin: 0 0 0 0;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Text Areas - FIXED SPACING */
        .stTextArea {
            margin-bottom: 0 !important;
        }
        
        .stTextArea > div {
            margin-bottom: 0 !important;
        }
        
        .stTextArea > div > div {
            margin-bottom: 0 !important;
        }
        
        /* This is the key fix - targeting the wrapper around textarea */
        .stTextArea > div > div > div {
            margin-bottom: 0 !important;
        }
        
        /* Force exact height and spacing for textarea container */
        .stTextArea {
            height: 420px !important;
        }
        
        .stTextArea > div > div {
            height: 420px !important;
        }
        
        .stTextArea > div > div > textarea {
            background-color: #ffffff !important;
            border: 1px solid #3730a3 !important;
            border-top: none !important;
            border-radius: 0 !important;
            border-bottom: none !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            color: #1e293b !important;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
            resize: none !important;
            padding: 1rem !important;
            caret-color: #1e293b !important;
            margin-bottom: 0 !important;
            height: 420px !important;
            box-sizing: border-box !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #1e3a8a !important;
            box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.2) !important;
            outline: none !important;
        }
        
        /* Additional fix for any nested containers */
        .stTextArea [data-testid="stWidgetLabel"] {
            display: none !important;
        }
        
        /* Ensure no gap between textarea container and stats bar */
        .element-container:has(.stTextArea) {
            margin-bottom: 0 !important;
        }
        
        .element-container:has(.stTextArea) + div {
            margin-top: 0 !important;
        }
        
        /* Output Container */
        .output-container {
            background: #ffffff;
            border: 1px solid #3730a3;
            border-top: none;
            border-radius: 0 0 6px 6px;
            height: 420px; /* Same height as textarea */
            overflow-y: auto !important;
            overflow-x: hidden !important;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #1e293b;
            word-wrap: break-word !important;
            white-space: pre-wrap !important;
            margin-bottom: 0 !important;
            box-sizing: border-box;
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
            display: inline-block;
        }
        
        /* Button Styles */
        .stButton {
            margin-top: 0.5rem !important;
            margin-bottom: 0 !important;
        }
        
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
            width: 100% !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Download Button - Fixed text color to always be white */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #1e3a8a, #1e40af) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 3px 6px rgba(30, 58, 138, 0.3) !important;
            width: 100% !important;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 12px rgba(30, 58, 138, 0.4) !important;
            color: white !important;
        }
        
        .stDownloadButton > button:active {
            transform: translateY(0) !important;
            color: white !important;
        }
        
        /* Force exact alignment for both stats bars */
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
            margin-bottom: 0.5rem;
            margin-top: 0 !important;
            height: 38px; /* Fixed height for alignment */
            box-sizing: border-box;
            position: relative;
            top: 0;
        }
        
        /* Force both columns to have identical element spacing */
        .stColumn .element-container {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Specific targeting for the stats bar containers */
        .stColumn > div > div:has(.stats-bar) {
            margin-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        /* Sidebar Styles */
        div[class^="css"][data-testid="stSidebar"]{
            background: #f8fafc !important;
            border-right: 1px solid #3730a3 !important;
            padding: 1rem !important;
            height: 100vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        
        .sidebar-section {
            background: white;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(30, 58, 138, 0.1);
            border: 1px solid #e2e8f0;
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
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Comprehensive element spacing control */
        .element-container {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Force identical spacing in both columns */
        .stColumn .element-container {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
            padding-bottom: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Additional reset for any nested containers */
        .stColumn > div {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        .stColumn > div > div {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Specific fix for markdown containers (where stats-bar lives) */
        .stMarkdown {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        .stMarkdown > div {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Footer */
        .footer-section {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
        }

        /* Responsive design for header */
        @media (max-width: 768px) {
            .header-container {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
            
            .header-content {
                margin-left: 0;
            }
            
            .logo-container {
                min-width: auto;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Header Section with Logo
# You can either use a local image file or upload the logo to your project
# For this example, I'll show both methods

# Method 1: Using local image file (recommended)
# Save your logo image as "logo.png" in the same directory as your app.py
logo_base64 = get_base64_of_image("logo.png")  # Change this to your logo file path

# Method 2: If you want to embed the logo directly in code (alternative)
# You can convert your logo to base64 and paste it here
# logo_base64 = "your_base64_encoded_logo_string_here"

if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Howe Robinson Partners Logo">'
else:
    # Fallback if logo file is not found
    logo_html = '<div style="color: white; font-size: 12px; text-align: center;">Logo<br>Here</div>'

st.markdown(f"""
    <div class='header-container'>
        <div class='logo-container'>
            {logo_html}
        </div>
        <div class='header-content'>
            <h1 class='main-title'>NEMO</h1>
            <p class='subtitle'>Transform abbreviated text into fully expanded, professional content</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Load abbreviation dictionary
if uploaded_file:
    abbr_dict = load_abbreviation_dict(uploaded_file)
else:
    abbr_dict = load_abbreviation_dict("abbreviations_01.12.25.xlsx")

# Initialize clear counter for forcing text area reset
if "clear_counter" not in st.session_state:
    st.session_state.clear_counter = 0

# Main Content Area - Changed gap from "large" to "medium"
col1, col2 = st.columns(2, gap="medium")

# Left Column: Original Text Input
with col1:
    st.markdown("""
        <div class='section-header'>
            📝 Original Text
        </div>
    """, unsafe_allow_html=True)
    
    original_text = st.text_area("", height=420, key=f"input_text_{st.session_state.clear_counter}", label_visibility="collapsed")
    
    # Stats for original text
    char_count = len(original_text) if original_text else 0
    word_count = len(original_text.split()) if original_text and original_text.strip() else 0
    
    st.markdown(f"""
        <div class='stats-bar'>
            <div class='stat-item'>📊 Characters: {char_count}</div>
            <div class='stat-item'>📝 Words: {word_count}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Buttons below the first box (Original Text)
    col1_btn1, col1_btn2 = st.columns(2, gap="small")
    
    with col1_btn1:
        expand_clicked = st.button("🔄 Expand Text", use_container_width=True)
    
    with col1_btn2:
        if "expanded" in st.session_state:
            st.download_button(
                label="⬇️ Download",
                data=st.session_state["expanded"],
                file_name="expanded_text.txt",
                mime="text/plain",
                use_container_width=True
            )

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
    
    # Buttons below the second box (Expanded Text)
    if "expanded" in st.session_state:
        col2_btn1, col2_btn2 = st.columns(2, gap="small")

        with col2_btn1:
            if st.button("🗑️ Clear", key="clear_out", use_container_width=True):
                # Clear both columns by removing all relevant session state
                st.session_state.pop("expanded", None)
                st.session_state.pop("highlighted", None)
                # Increment counter to force text area reset
                st.session_state.clear_counter += 1
                st.rerun()

        with col2_btn2:
            import json
            escaped_text = json.dumps(st.session_state["expanded"])[1:-1]

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
                style="background: linear-gradient(135deg, #1e3a8a, #1e40af); color: white; border: none; border-radius: 6px; padding: 0.6rem 1.2rem; font-weight: 600; font-size: 13px; width: 100%; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 3px 6px rgba(30, 58, 138, 0.3);">
                📋 Copy to Clipboard
            </button>
            """
            st.components.v1.html(copy_js, height=50)

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