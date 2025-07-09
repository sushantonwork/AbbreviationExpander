import io, json, html, re
import streamlit as st
from docx import Document                # python‑docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from expander import load_abbreviation_dict, expand_abbreviations

# ─────────────────────────────────────────────────────────────────────────────
# Helper ─ identify real clause headings only - IMPROVED VERSION
# ─────────────────────────────────────────────────────────────────────────────

# Updated regex to handle the actual document format
HEADER_RE = re.compile(r"^\s*(\d{1,3})\\?[\.\:\-]\s*(.*)$")
# Additional regex to handle existing "Clause X" format with various separators
CLAUSE_RE = re.compile(r"^\s*[Cc]lause\s+(\d{1,3})[\.\:\-]?\s*(.*)$", re.IGNORECASE)

def is_clause_heading(text: str, expected: int | None) -> tuple[bool, int | None]:
    """
    Returns (True,new_expected) if *text* is the next main‑clause heading.
    • Headings must be consecutive numbers (30→31→32 …).
    • Must be reasonable length (≤30 words) and not contain obvious paragraph text
    • Also handles numbered clauses without titles (e.g., "91.")
    • Also handles existing "Clause X" format (e.g., "Clause 31. Trading Limits")
    """
    # Try both regex patterns
    m = HEADER_RE.match(text.strip())
    clause_m = CLAUSE_RE.match(text.strip())
    
    # Use whichever pattern matches
    if clause_m:
        m = clause_m
    elif not m:
        return (False, expected)

    num, title = int(m.group(1)), m.group(2).strip()

    # More flexible consecutive numbering - allow some gaps but prefer consecutive
    if expected is None:
        expected = num          # first heading sets the baseline
    
    # Allow for reasonable clause numbers (don't be too strict about perfect sequence)
    if expected is not None and num < expected:
        return (False, expected)  # Don't go backwards
    
    # Be more lenient with gaps for higher numbered clauses (90+)
    max_gap = 10 if num >= 90 else 5
    if expected is not None and num > expected + max_gap:
        return (False, expected)

    # Handle different cases based on title content
    words = title.split()
    
    # Case 1: No title at all (e.g., "91." or "Clause 91")
    if len(words) == 0:
        return (True, num + 1)
    
    # Case 2: Very short title (1-2 words) - likely legitimate clauses
    if len(words) <= 2:
        # Accept short titles like "Deleted" or legitimate short clause names
        return (True, num + 1)
    
    # Case 3: Long text that looks like paragraph content
    if len(words) > 30:
        return (False, expected)
    
    # Case 4: Text starting with obvious sentence starters - likely paragraph text
    paragraph_starters = [
        'if', 'when', 'should', 'the charterers shall', 'the owners shall',
        'in case', 'notwithstanding', 'subject to', 'provided that',
        'it is understood that', 'all', 'any', 'referring to', 'during the'
    ]
    
    title_lower = title.lower()
    if any(title_lower.startswith(starter) for starter in paragraph_starters):
        return (False, expected)
    
    # Case 5: Text with too many sentence indicators - likely paragraph text
    sentence_indicators = ['shall', 'will', 'must', 'should', 'may', 'can']
    indicator_count = sum(1 for indicator in sentence_indicators if indicator in title_lower)
    if indicator_count > 1:  # More than one indicates sentence text
        return (False, expected)
    
    # Case 6: Accept if it looks like a proper heading
    return (True, num + 1)

def clean_header_text(text: str) -> str:
    """Clean and format header text for display"""
    # Remove escape characters
    text = text.replace('\\', '')
    # Remove leading colons, dashes, and extra spaces
    text = re.sub(r'^[\:\-\s]+', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

# ─────────────────────────────────────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="NEMO • Word Formatter", layout="wide")
st.title("🛠 Word Formatter + Abbreviation Expander")

# 1️⃣  Abbreviation dictionary ------------------------------------------------
dict_file = st.sidebar.file_uploader("Upload custom abbreviation dictionary (.xlsx)", type=["xlsx"])
if dict_file:
    st.sidebar.success("Custom dictionary loaded!", icon="✅")
    abbr_dict = load_abbreviation_dict(dict_file)
else:
    abbr_dict = load_abbreviation_dict("abbreviations4thJuly.xlsx")
    st.sidebar.info("Using default dictionary")

# 2️⃣  User input -------------------------------------------------------------
raw_text = st.text_area("Paste or type your Word text here 👇",
                        height=400, label_visibility="collapsed",
                        key="riders_input")

chars = len(raw_text)
words = len(raw_text.split()) if raw_text.strip() else 0
st.caption(f"**Characters:** {chars}   **Words:** {words}")

# --------------------------------------------------------------------------- #
# 3️⃣  Expand + format on button click
# --------------------------------------------------------------------------- #
col_go, col_dl = st.columns(2, gap="small")

with col_go:
    go = st.button("🚀 Expand & Format", use_container_width=True)

formatted_bytes = None            # <- will hold .docx
preview_lines   = []              # <- for the HTML preview

if go:
    if not raw_text.strip():
        st.warning("Please enter some text before formatting.")
    else:
        with st.spinner("Expanding abbreviations and creating Word document…"):

            # --- 1. expand abbreviations (plain) ---------------------------
            expanded_plain, _ = expand_abbreviations(raw_text, abbr_dict)
            
            from expander import normalize_slashes
            expanded_plain = normalize_slashes(expanded_plain)
            
            # --- 2. build .docx in memory ----------------------------------
            doc   = Document()
            style = doc.styles["Normal"]
            style.font.name = "Arial"
            style.font.size = Pt(10)

            expected_clause_num = None
            
            for line in expanded_plain.splitlines():

                # Skip blank lines entirely
                if not line.strip():
                    preview_lines.append("")        # keep blank for preview
                    continue

                # Check if this line is a clause heading (handles both "31." and "Clause 31" formats)
                is_header, expected_clause_num = is_clause_heading(line, expected_clause_num)
                
                if is_header:
                    # Extract number and title using both possible regex patterns
                    m = HEADER_RE.match(line.strip())
                    clause_m = CLAUSE_RE.match(line.strip())
                    
                    # Use whichever pattern matched
                    if clause_m:
                        num = clause_m.group(1)
                        title = clean_header_text(clause_m.group(2))
                    else:
                        num = m.group(1)
                        title = clean_header_text(m.group(2))
                        
                    # Determine if we should include the title or treat it as separate paragraph
                    should_include_title = True
                    remaining_text = ""
                    
                    words = title.split()
                    
                    # Check if title looks like paragraph text that got captured
                    if len(words) > 10:  # Long text - likely paragraph
                        should_include_title = False
                        remaining_text = title
                    elif title.lower().startswith(('in case', 'if', 'referring to', 'during the', 'where and when', 'should the')):
                        should_include_title = False
                        remaining_text = title
                    
                    # Format the clause header consistently (always CAPS, bold, underlined)
                    if not should_include_title or not title or title.lower() == 'deleted':
                        clause_text = f"CLAUSE {num}"
                        if title.lower() == 'deleted':
                            clause_text += ". DELETED"
                    else:
                        clause_text = f"CLAUSE {num}. {title.upper()}"

                    # docx – header
                    p   = doc.add_paragraph()
                    run = p.add_run(clause_text)
                    run.bold      = True
                    run.underline = True

                    # paragraph formatting
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after  = Pt(10)
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

                    # preview
                    preview_lines.append(
                        f"<b><u>{html.escape(clause_text)}</u></b>"
                    )
                    
                    # If we have remaining text that should be a separate paragraph, add it
                    if remaining_text:
                        p = doc.add_paragraph(remaining_text)
                        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        p.paragraph_format.space_before = Pt(0)
                        p.paragraph_format.space_after  = Pt(10)
                        run = p.runs[0]
                        run.font.name = "Arial"
                        run.font.size = Pt(10)
                        
                        preview_lines.append(html.escape(remaining_text))
                else:
                    # regular paragraph
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after  = Pt(10)
                    run = p.runs[0]
                    run.font.name = "Arial"
                    run.font.size = Pt(10)

                    preview_lines.append(html.escape(line))

            # save the document
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            formatted_bytes = bio.read()

        # --- 3. live preview ---------------------------------------------
        st.subheader("Preview")
        st.markdown(
            "<div style='background:#fff;border:1px solid #3730a3;"
            "padding:1rem;border-radius:6px;white-space:pre-wrap;"
            "font-family:Arial;font-size:10pt;color:#1e293b;"
            "text-align:justify'>" + "<br>".join(preview_lines) + "</div>",
            unsafe_allow_html=True,
        )

# 4️⃣  Download + copy --------------------------------------------------------
if formatted_bytes:
    with col_dl:
        st.download_button("⬇️ Download .docx",
                           data=formatted_bytes,
                           file_name="formatted_text.docx",
                           mime=("application/vnd.openxmlformats-officedocument."
                                 "wordprocessingml.document"),
                           use_container_width=True)

    escaped = json.dumps(expanded_plain)[1:-1]
    copy_js = f"""
    <script>
    function copyWordText(){{
        navigator.clipboard.writeText("{escaped}").then(
            () => {{
                const btn = document.getElementById("copyWordBtn");
                btn.innerText="✅ Copied!";
                setTimeout(()=>btn.innerText="📋 Copy text",2000);
            }},
            () => alert("Copy failed – please try again."));
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