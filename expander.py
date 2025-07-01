import pandas as pd
import re

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

            plain_line = abbr_pattern.sub(replace_abbr_plain, plain_line)
            highlighted_line = abbr_pattern.sub(replace_abbr_highlighted, highlighted_line)

            # --- Final Formatting ---
            plain_line = capitalize_after_punctuation(plain_line)
            highlighted_line = capitalize_after_punctuation(highlighted_line)

            plain_lines.append(plain_line)
            highlighted_lines.append(highlighted_line)

        return "\n".join(plain_lines), "\n".join(highlighted_lines)

    return highlight_expansion(text)