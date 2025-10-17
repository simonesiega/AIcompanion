import re


def format_response(text: str) -> str:
    """
    Converte un testo formattato in stile Markdown in una versione HTML.


    Funzionalità:
    - Converte **testo** in <b>testo</b> (grassetto)
    - Converte *testo* in <i>testo</i> (corsivo)
    - Riconosce liste puntate con `*` o `-` e le trasforma in <ul><li>...</li></ul>
    - Sostituisce ritorni a capo con <br>
    - Riduce sequenze di più newline (\n\n\n) a un solo newline
    - Elimina spazi multipli consecutivi


    Args:
        text (str): Il testo sorgente da formattare.


    Returns:
        str: Una stringa HTML pulita.


    Esempi:
        >>> format_response("**Ciao**\nCome *va*?")
        '<b>Ciao</b><br>Come <i>va</i>?'


        >>> format_response("* elemento 1\\n* elemento 2")
        '<ul><li>elemento 1</li><li>elemento 2</li></ul>'
    """


    # Se il testo è vuoto o None, restituisce una stringa vuota
    if not text: return ""
    text = text.strip()


    # Trasforma il testo racchiuso tra **...** in grassetto (<b>...</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Trasforma il testo racchiuso tra *...* in corsivo (<i>...</i>)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)


    # Suddivide il testo in righe per analizzare eventuali elementi di lista
    lines = text.splitlines()
    new_lines = []  
    is_list = False  


    for line in lines:
        line_stripped = line.strip()  # elimina spazi superflui da ogni riga


        # Se la riga inizia con "*" o "-" seguita da spazio e testo
        if re.match(r'^(\*|-)\s+.+', line_stripped):
            # Se è il primo elemento di una lista, apre il tag <ul>
            if not is_list:
                new_lines.append("<ul>")
                is_list = True


            # Rimuove il simbolo iniziale ("*" o "-") e aggiunge <li>...</li>
            item = re.sub(r'^(\*|-)\s+', '', line_stripped)
            new_lines.append(f"<li>{item}</li>")
        else:
            # Se in una lista viene trovata una riga normale, chiude </ul>
            if is_list:
                new_lines.append("</ul>")
                is_list = False


            # Aggiunge la riga
            new_lines.append(line_stripped)


    # Se il testo finisce con una lista aperta, chiude l'ultimo </ul>
    if is_list: new_lines.append("</ul>")
    # Riunisce tutte le righe in un'unica stringa con \n come separatore
    text = "\n".join(new_lines)


    # Converte più ritorni a capo consecutivi (\n\n, \n\n\n, ecc.) in un solo \n
    text = re.sub(r'\n{2,}', '\n', text)
    # Sostituisce ogni ritorno a capo singolo con un tag HTML <br>
    text = text.replace("\n", "<br>")


    # Rimuove spazi multipli consecutivi
    text = re.sub(r'\s{2,}', ' ', text)


    # Restituisce il testo HTML finale
    return text



