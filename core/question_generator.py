import json
import os
import re
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore

# Import delle configurazioni globali
from core.config import (
    TestChatConfig,
    EmbeddingConfig,
)


def create_interrogation(db_paths: list, n_questions: int = TestChatConfig.N_QUESTIONS):
    """
    Genera un set di domande basandosi su:
    - uno o più database vettoriali (.db)
    - il file di contesto interrogazione/contesto.json

    Parametri:
    ----------
    db_paths : list
        Lista di percorsi ai file .db.

    n_questions : int
        Numero di domande da generare (default = 10)

    Output
    ------
    Crea (o sovrascrive) il file:
        ../interrogazione/domande.json
    con struttura:
        {
            "topic": "...",
            "questions": [ ... ]
        }
    """

    # print(f"Avvio generazione interrogazione usando {len(db_paths)} DB...")

    # Inizializza embeddings
    embeddings = OllamaEmbeddings(model=EmbeddingConfig.NAME)

    vectorstores = []
    # Caricamento dei DB e unione
    for path in db_paths:
        if not os.path.exists(path):
            print(f"DB non trovato e ignorato: {path}")
            continue

        # print(f"Caricamento DB: {path}")
        vs = InMemoryVectorStore.load(path=path, embedding=embeddings)
        vectorstores.append(vs)

    # Nessun db é stato letto correttamente
    if not vectorstores:
        raise RuntimeError("Nessun DB valido è stato caricato.")

    # Merge dei VectorStore (se > 1 altrimenti main_vs = vectorstores[0] = vs)
    main_vs = vectorstores[0]
    for vs in vectorstores[1:]:
        main_vs.merge_from(vs)
    # print("Unione dei .db avvenuti con successo.")

    if not os.path.exists(TestChatConfig.CONTEXT_PATH):
        raise FileNotFoundError(f"File contesto non trovato: {TestChatConfig.CONTEXT_PATH}")

    with open(TestChatConfig.CONTEXT_PATH, "r", encoding="utf-8") as f:
        contesto = json.load(f)

    topic = contesto.get("topic", "").strip()
    content = contesto.get("content", "").strip()

    # Struttura del contesto non corretta\
    # deve essere del tipo {
    #      "topic": "...",
    #      "content": "...",
    #  }
    if not topic or not content:
        raise ValueError(
            "Il file contesto JSON deve contenere:\n"
            '{ "topic": "...", "content": "..." }'
        )
    # print(f"Contesto caricato. Topic: {topic}")

    # Similarity search nel DB
    docs = main_vs.similarity_search(topic, k=7)

    combined_docs = "\n".join(d.page_content for d in docs)

    # Testo finale usato dal modello
    final_context = content + "\n\n---\n\n" + combined_docs

    # Costruzione del prompt di sistema
    prompt = f"""
    Sei un assistente che genera domande.

    DEVI utilizzare obbligatoriamente entrambe le seguenti fonti:

    DOCUMENTI DAL DATABASE (OBBLIGATORI):
    {combined_docs}

    CONTESTO AGGIUNTIVO (OBBLIGATORIO):
    {content}

    Regole IMPORTANTI:
    - Devi integrare sia il DB sia il contesto.
    - Nessuna delle due fonti può essere ignorata.
    - Le domande devono essere legate al topic: {topic}
    - Numero di domande: {n_questions}
    - Tipologie varie: definizione, spiegazione, funzionamento, esempi, comprensione.

    RISPOSTA:
    Restituisci SOLO un array JSON:
    ["Domanda 1...", "Domanda 2...", ...]
    """

    # Inizializzazione LLM 
    llm = OllamaLLM(
        model=TestChatConfig.MODEL_NAME,
        temperature=0,     
        reasoning=False
    )

    # Invocazione modello
    response = llm.invoke(prompt)

    # Parsing JSON (gestisce anche JSON non validi)
    try:
        # Parsing diretto
        questions = json.loads(response)
    except Exception:
        # Match array JSON nella risposta
        match = re.search(r"\[.*\]", response, flags=re.S)
        if match:
            questions = json.loads(match.group(0))
        
        # Fallback finale
        else:
            questions = [
                l.strip() for l in response.split("\n")
                if len(l.strip()) > 5
            ]
    print(f"Domande generate: {len(questions)}")

    # Salvataggio domande
    os.makedirs(TestChatConfig.INTERROGATION_DIR, exist_ok=True)
    with open(TestChatConfig.QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump({"topic": topic, "questions": questions}, f, ensure_ascii=False, indent=2)

# Test
if __name__ == "__main__":
    """
    Esempio di uso
    Usa il DB di Alice nel Paese delle Meraviglie
    """
    db_test = ["../vs/alice.db"]
    create_interrogation(db_test)
