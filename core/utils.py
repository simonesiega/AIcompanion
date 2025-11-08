import re

def format_for_html(text: str) -> str:
    """Formatta il testo in HTML."""
    if not text: return ""
    text = text.strip()

    # Grassetto e corsivo
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)

    # Liste
    lines = text.splitlines()
    new_lines = []
    is_list = False
    for line in lines:
        line_stripped = line.strip()
        if re.match(r'^(\*|-)\s+.+', line_stripped):
            if not is_list:
                new_lines.append("<ul>")
                is_list = True
            item = re.sub(r'^(\*|-)\s+', '', line_stripped)
            new_lines.append(f"<li>{item}</li>")
        else:
            if is_list:
                new_lines.append("</ul>")
                is_list = False
            new_lines.append(line_stripped)
    if is_list: new_lines.append("</ul>")
    text = "\n".join(new_lines)

    # Nuove linee e spazi
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.replace("\n", "<br>")
    text = re.sub(r'\s{2,}', ' ', text)
    return text


def format_for_tts(text: str) -> str:
    """Rimuove Markdown e HTML per generare un testo pulito per TTS."""
    if not text: return ""
    text = text.strip()

    # Rimuove grassetto/corsivo Markdown
    text = re.sub(r'\*\*.*?\*\*', '', text)
    text = re.sub(r'\*.*?\*', '', text)

    # Rimuove eventuali tag HTML
    text = re.sub(r'<.*?>', '', text)
    
    # Collassa spazi e ritorni a capo multipli
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()
