import streamlit as st
import pyperclip
from expander import load_abbreviation_dict, expand_abbreviations

# Set Streamlit page configuration
st.set_page_config(page_title="Abbreviation Expander", layout="wide")

# Sidebar file upload
uploaded_file = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

# Load abbreviation dictionary
if uploaded_file:
    abbr_dict = load_abbreviation_dict(uploaded_file)
else:
    abbr_dict = load_abbreviation_dict("abbreviations3.xlsx")

# Define two columns
col1, col2 = st.columns(2)

# Left Column: Original Text
with col1:
    st.markdown("### Original Text")
    original_text = st.text_area(" ", height=600, key="input_text")

# Right Column: Expanded Text
with col2:
    st.markdown("### Expanded Text")

    # Buttons aligned side by side
    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        expand_clicked = st.button("🔁 Expand Abbreviations")

    with btn_col2:
        copy_clicked = st.button("📋 Copy Expanded Text")

    # Process abbreviation expansion
    if expand_clicked:
        if not original_text.strip():
            st.warning("Please enter some text to expand.")
        else:
            expanded_text, highlighted_text = expand_abbreviations(original_text, abbr_dict)
            st.session_state["expanded"] = expanded_text
            st.session_state["highlighted"] = highlighted_text

    # Display the expanded and highlighted text
    if "highlighted" in st.session_state:
        st.markdown("Result", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='padding: 10px; background-color: #1e1e1e; border: 1px solid #21c55d;
                        border-radius: 5px; color: white; height: 530px; overflow-y: auto;'>
                {st.session_state["highlighted"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Handle copy button
    if copy_clicked and "expanded" in st.session_state:
        pyperclip.copy(st.session_state["expanded"])
        st.success("✅ Text copied to clipboard!")
