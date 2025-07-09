import pandas as pd
import re

def normalize_slashes(text: str, highlight=False) -> str:
    """
    Normalizes:
    - 'and / or' → 'and/or'
    - 'word1 / word2 / word3' etc. → single spaced slashes
    If highlight=True, wrap changed parts in <mark> tags.
    """

    # 1. Handle "and / or" → "and/or"
    def fix_and_or(m):
        return "<mark>and/or</mark>" if highlight else "and/or"
    text = re.sub(r'\band\s*/\s*or\b', fix_and_or, text, flags=re.IGNORECASE)

    # 2. Normalize multiple slashes
    def fix_multiple(m):
        parts = re.split(r'\s*/\s*', m.group())
        fixed = ' / '.join(parts)
        return f"<mark>{fixed}</mark>" if highlight else fixed
    text = re.sub(r'(\w+\s*/\s*\w+(?:\s*/\s*\w+)+)', fix_multiple, text)

    # 3. Normalize single slash phrases
    def fix_single(m):
        a, b = m.group(1), m.group(2)
        if a.lower() == "and" and b.lower() == "or":
            return "<mark>and/or</mark>" if highlight else "and/or"
        fixed = f"{a} / {b}"
        return f"<mark>{fixed}</mark>" if highlight else fixed
    text = re.sub(r'\b(\w+)\s*/\s*(\w+)\b', fix_single, text)

    return text

def load_abbreviation_dict(excel_file):
    df = pd.read_excel(excel_file)
    return {k.strip().lower(): v.strip() for k, v in zip(df['Abbreviation'], df['Full Form'])}

def expand_abbreviations(text, abbr_dict):
    def capitalize_after_punctuation(text):
        return re.sub(r'([.!?])(\s*)([a-z])', lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)

    def highlight_expansion(original_text):
        lines = original_text.splitlines()
        highlighted_lines = []
        plain_lines = []

        # Sort abbreviation keys by length descending for longest matching
        sorted_keys = sorted(abbr_dict.keys(), key=len, reverse=True)
        escaped_keys = [re.escape(k) for k in sorted_keys]
        abbr_pattern = re.compile(r'(?<!\w)(' + '|'.join(escaped_keys) + r')(?!\w)', re.IGNORECASE)

        for line in lines:
            # --- Number + Abbr Replacements ---
            def replace_number_abbr_plain(match):
                quantity = match.group(1)
                abbr = match.group(2)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)
                if full_form:
                    try:
                        if float(quantity) < 1.01:
                            full_form = re.sub(r'\btons\b', 'ton', full_form, flags=re.IGNORECASE)
                    except ValueError:
                        pass
                    return f"{quantity} {full_form}"
                return match.group(0)

            def replace_number_abbr_highlighted(match):
                quantity = match.group(1)
                abbr = match.group(2)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)
                if full_form:
                    try:
                        if float(quantity) < 1.01:
                            full_form = re.sub(r'\btons\b', 'ton', full_form, flags=re.IGNORECASE)
                    except ValueError:
                        pass
                    return f"<mark>{quantity} {full_form}</mark>"
                return match.group(0)

            plain_line = re.sub(r'\b(\d*\.?\d+)\s*([a-zA-Z().]+)\b', replace_number_abbr_plain, line)
            highlighted_line = re.sub(r'\b(\d*\.?\d+)\s*([a-zA-Z().]+)\b', replace_number_abbr_highlighted, line)

            # --- Pure Abbreviation Replacements ---
            def replace_abbr_plain(match):
                abbr = match.group(0)
                full_form = abbr_dict.get(abbr.lower())
                return full_form if full_form else abbr

            def replace_abbr_highlighted(match):
                abbr = match.group(0)
                full_form = abbr_dict.get(abbr.lower())
                return f"<mark>{full_form}</mark>" if full_form else abbr
            
            def avoid_nested_mark(text):
                # Fix nested <mark> tags like <mark><mark>text</mark></mark> → <mark>text</mark>
                text = re.sub(r'<mark><mark>(.*?)</mark></mark>', r'<mark>\1</mark>', text)
                return text

            plain_line = abbr_pattern.sub(replace_abbr_plain, plain_line)
            highlighted_line = abbr_pattern.sub(replace_abbr_highlighted, highlighted_line)

            # --- Final Formatting ---
            plain_line = capitalize_after_punctuation(plain_line)
            highlighted_line = capitalize_after_punctuation(highlighted_line)

            plain_line = normalize_slashes(plain_line, highlight=False)
            highlighted_line = normalize_slashes(highlighted_line, highlight=True)

            highlighted_line = avoid_nested_mark(highlighted_line)

            plain_lines.append(plain_line)
            highlighted_lines.append(highlighted_line)

        return "\n".join(plain_lines), "\n".join(highlighted_lines)

    return highlight_expansion(text)