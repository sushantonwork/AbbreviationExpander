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

        for line in lines:
            original_line = line

            def replace_number_abbr(match):
                quantity = match.group(1)
                abbr = match.group(2)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)

                if full_form:
                    try:
                        qty_float = float(quantity)
                        if qty_float < 1.01:
                            full_form = re.sub(r'\btons\b', 'ton', full_form, flags=re.IGNORECASE)
                    except ValueError:
                        pass
                    return f"<mark>{quantity} {full_form}</mark>"
                return match.group(0)

            line_with_numbers = re.sub(r'\b(\d*\.?\d+)\s*([a-zA-Z]+)\b', replace_number_abbr, line)

            def replace_abbr(match):
                abbr = match.group(0)
                abbr_key = abbr.lower()
                full_form = abbr_dict.get(abbr_key)
                return f"<mark>{full_form}</mark>" if full_form else abbr

            abbr_pattern = re.compile(
                r'\b(' + '|'.join(re.escape(k) for k in sorted(abbr_dict, key=len, reverse=True)) + r")\b(?!\.)",
                re.IGNORECASE
            )

            highlighted = abbr_pattern.sub(replace_abbr, line_with_numbers)
            highlighted = capitalize_after_punctuation(highlighted)
            plain = re.sub(r'<mark>(.*?)</mark>', r'\1', highlighted)

            highlighted_lines.append(highlighted)
            plain_lines.append(plain)

        return "\n".join(plain_lines), "\n".join(highlighted_lines)

    return highlight_expansion(text)
