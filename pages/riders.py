import io
import json
import html
import streamlit as st
from docx import Document                       # python-docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from expander import load_abbreviation_dict, expand_abbreviations

# ---- PAGE CONFIG -----------------------------------------------------------
st.set_page_config(page_title="NEMO • Word Formatter", layout="wide")
st.title("🛠 Word Formatter + Abbreviation Expander")

# --------------------------------------------------------------------------- #
# 1️⃣  Load abbreviation dictionary (re‑use the same logic you have)
# --------------------------------------------------------------------------- #
dict_file = st.sidebar.file_uploader(
    "Upload custom abbreviation dictionary (.xlsx)", type=["xlsx"]
)
if dict_file:
    st.sidebar.success("Custom dictionary loaded!", icon="✅")
    abbr_dict = load_abbreviation_dict(dict_file)
else:
    abbr_dict = load_abbreviation_dict("abbreviations4thJuly.xlsx")
    st.sidebar.info("Using default dictionary")

# --------------------------------------------------------------------------- #
# 2️⃣  User input
# --------------------------------------------------------------------------- #
raw_text = st.text_area(
    "Paste or type your Word text here 👇",
    height=400,
    label_visibility="collapsed",
    key="riders_input",
)

# live character / word count
chars = len(raw_text)
words = len(raw_text.split()) if raw_text.strip() else 0
st.caption(f"**Characters:** {chars}   **Words:** {words}")

# --------------------------------------------------------------------------- #
# 3️⃣  Expand + format on button click
# --------------------------------------------------------------------------- #
col_go, col_dl = st.columns(2, gap="small")

with col_go:
    go = st.button("🚀 Expand & Format", use_container_width=True)

formatted_bytes = None  # will hold the Word file if generated

if go:
    if not raw_text.strip():
        st.warning("Please enter some text before formatting.")
    else:
        with st.spinner("Expanding abbreviations and creating Word document…"):
            # --- expand abbreviations (plain version, no <mark> tags) --------
            expanded_plain, _ = expand_abbreviations(raw_text, abbr_dict)

            # --- build .docx in memory --------------------------------------
            doc = Document()
            style = doc.styles["Normal"]
            style.font.name = "Arial"
            style.font.size = Pt(10)            # 10 pt

            prev_blank = False
            for line in expanded_plain.splitlines():
                if not line.strip():
                    if prev_blank:
                        continue
                    prev_blank = True
                    p = doc.add_paragraph("")
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(10)
                    continue
                prev_blank = False
                p = doc.add_paragraph(line)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(10)

            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            formatted_bytes = bio.read()

        # preview (optional)
        st.subheader("Preview")
        st.markdown(
            f"<div style='background:#fff;border:1px solid #3730a3;"
            f"padding:1rem;border-radius:6px;white-space:pre-wrap;font-family:Arial;"
            f"font-size:10pt;color:#1e293b;text-align:justify'>{html.escape(expanded_plain)}</div>",
            unsafe_allow_html=True,
        )

# --------------------------------------------------------------------------- #
# 4️⃣  Download + copy‑to‑clipboard buttons
# --------------------------------------------------------------------------- #
if formatted_bytes:
    with col_dl:
        st.download_button(
            label="⬇️ Download .docx",
            data=formatted_bytes,
            file_name="formatted_text.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    # copy to clipboard (text, not docx) – keeps the same JS snippet style
    escaped = json.dumps(expanded_plain)[1:-1]
    copy_js = f"""
    <script>
    function copyWordText() {{
        navigator.clipboard.writeText("{escaped}").then(
            () => {{
                const btn = document.getElementById("copyWordBtn");
                btn.innerText = "✅ Copied!";
                setTimeout(() => btn.innerText = "📋 Copy text", 2000);
            }},
            () => alert("Copy failed – please try again.")
        );
    }}
    </script>
    <button id="copyWordBtn"
            onclick="copyWordText()"
            style="background:linear-gradient(135deg,#1e3a8a,#1e40af);color:#fff;
                   border:none;border-radius:6px;padding:0.6rem 1.2rem;
                   font-weight:600;font-size:13px;width:100%;margin-top:0.5rem;
                   box-shadow:0 3px 6px rgba(30,58,138,.3);cursor:pointer;">
        📋 Copy text
    </button>
    """
    st.components.v1.html(copy_js, height=55)