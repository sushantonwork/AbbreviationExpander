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
     # ✅ THIS is the fix — add re.IGNORECASE
    text = re.sub(r'\b(\w+)\s*/\s*(\w+)\b', fix_single, text, flags=re.IGNORECASE)

    return text

def load_abbreviation_dict(excel_file):
    df = pd.read_excel(excel_file)
    result = {}
    for abbr, full in zip(df['Abbreviation'], df['Full Form']):
        if pd.notna(abbr) and pd.notna(full):
            clean_abbr = str(abbr).strip().lower()
            clean_full = str(full).strip()
            if clean_abbr and clean_full:
                result[clean_abbr] = clean_full
    return result

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
            def avoid_nested_mark(text):
                # Simple but effective nested mark cleanup
                text = re.sub(r'<mark><mark>(.*?)</mark></mark>', r'<mark>\1</mark>', text)
                text = re.sub(r'<mark>(.*?)</mark></mark>', r'<mark>\1</mark>', text)
                text = re.sub(r'</mark>\s*<mark>', ' ', text)
                return text

            # Apply abbreviation expansion BEFORE slash normalization
            plain_line = line
            highlighted_line = line

            # More precise number + abbreviation pattern
            number_abbr_pattern = re.compile(r'\b(\d*\.?\d+)\s*([a-zA-Z()./]+)\b')
            
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

            # Pure abbreviation replacements - only replace if found in dictionary
            def replace_abbr_plain(match):
                abbr = match.group(0)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)
                return full_form if full_form else abbr

            def replace_abbr_highlighted(match):
                abbr = match.group(0)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)
                return f"<mark>{full_form}</mark>" if full_form else abbr

            # Apply expansions with more careful matching
            # First handle number + abbreviation patterns
            plain_line = number_abbr_pattern.sub(replace_number_abbr_plain, plain_line)
            
            # For highlighted text, avoid matching inside existing marks
            if '<mark>' not in highlighted_line:
                highlighted_line = number_abbr_pattern.sub(replace_number_abbr_highlighted, highlighted_line)
            else:
                # Split by existing marks and only process unmarked parts
                parts = re.split(r'(<mark>.*?</mark>)', highlighted_line)
                new_parts = []
                for part in parts:
                    if part.startswith('<mark>') and part.endswith('</mark>'):
                        new_parts.append(part)
                    else:
                        new_parts.append(number_abbr_pattern.sub(replace_number_abbr_highlighted, part))
                highlighted_line = ''.join(new_parts)

            # Handle standalone abbreviations with mark-aware processing
            if '<mark>' not in plain_line:
                plain_line = abbr_pattern.sub(replace_abbr_plain, plain_line)
            else:
                # Split by existing marks and only process unmarked parts
                parts = re.split(r'(<mark>.*?</mark>)', plain_line)
                new_parts = []
                for part in parts:
                    if part.startswith('<mark>') and part.endswith('</mark>'):
                        new_parts.append(part)
                    else:
                        new_parts.append(abbr_pattern.sub(replace_abbr_plain, part))
                plain_line = ''.join(new_parts)
            
            if '<mark>' not in highlighted_line:
                highlighted_line = abbr_pattern.sub(replace_abbr_highlighted, highlighted_line)
            else:
                # Split by existing marks and only process unmarked parts
                parts = re.split(r'(<mark>.*?</mark>)', highlighted_line)
                new_parts = []
                for part in parts:
                    if part.startswith('<mark>') and part.endswith('</mark>'):
                        new_parts.append(part)
                    else:
                        new_parts.append(abbr_pattern.sub(replace_abbr_highlighted, part))
                highlighted_line = ''.join(new_parts)

            # Apply slash normalization AFTER expansion, but protect dictionary content
            # For plain text - apply normalization
            normalized_plain = normalize_slashes(plain_line, highlight=False)
            
            # Restore any dictionary expansions that got normalized
            for abbr_key in sorted_keys:
                full_form = abbr_dict[abbr_key]
                if '/' in full_form:
                    # If normalization changed this dictionary entry, restore it
                    normalized_form = normalize_slashes(full_form, highlight=False)
                    if normalized_form != full_form:
                        normalized_plain = normalized_plain.replace(normalized_form, full_form)

            # For highlighted text
            normalized_highlighted = normalize_slashes(highlighted_line, highlight=True)
            
            # Restore dictionary expansions in highlighted text
            for abbr_key in sorted_keys:
                full_form = abbr_dict[abbr_key]
                if '/' in full_form:
                    marked_original = f"<mark>{full_form}</mark>"
                    marked_normalized = f"<mark>{normalize_slashes(full_form, highlight=False)}</mark>"
                    if marked_normalized != marked_original:
                        normalized_highlighted = normalized_highlighted.replace(marked_normalized, marked_original)

            # Final formatting
            plain_line = capitalize_after_punctuation(normalized_plain)
            highlighted_line = capitalize_after_punctuation(normalized_highlighted)
            highlighted_line = avoid_nested_mark(highlighted_line)

            plain_lines.append(plain_line)
            highlighted_lines.append(highlighted_line)

        return "\n".join(plain_lines), "\n".join(highlighted_lines)

    return highlight_expansion(text)