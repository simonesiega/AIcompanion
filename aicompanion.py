"""
aicompanion.py
--------------
Applicazione Flask che espone un endpoint di chat basato su modello LLM con Retrieval Augmented Generation (RAG).
Il sistema utilizza un modello Ollama per generare risposte e un Vector Store per recuperare contesto rilevante
dai documenti caricati.

Struttura:
- Configurazioni caricate da config.py
- Endpoint API per interagire con il modello
- Gestione del contesto conversazionale e recupero informazioni dai documenti
"""

# Lib/site-packages
from flask import Flask, request, jsonify, send_file, send_from_directory
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore

# Moduli locali
from core.config import ModelConfig, EmbeddingConfig, ChatConfig, WebConfig
from core.utils import format_response

import torch

# Imposta dispositivo GPU se disponibile, altrimenti CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Dispositivo scelto per il modello: {device}")  # Da commentare

# Inizializzazione applicazione Flask
app = Flask(__name__, static_folder = WebConfig.STATIC_FOLDER)

# Inizializzazione del modello di chat
model = ChatOllama(
    model = ModelConfig.NAME,
    temperature  = ModelConfig.TEMPERATURE,
    reasoning = ModelConfig.REASONING,
    device = device
)

# Inizializzazione embeddings e vectorstore
embeddings = OllamaEmbeddings(
    model = EmbeddingConfig.NAME,
)

print("Test device per modello:", device)
print("CUDA disponibile:", torch.cuda.is_available())

# Caricamento del database vettoriale da file
vector_store = InMemoryVectorStore.load("./vs/alice.db", embedding = embeddings)
retriever = vector_store.as_retriever()

# Memoria della cronologia conversazionale
# Formato: [('human', 'messaggio'), ('assistant', 'risposta')]
chat_history = []


# Funzione per la costruzione del contesto del modello
def create_context(user_message: str, retrieved_documents: str, history: list) -> list:
    """
    Costruisce il contesto da fornire al modello AI.

    :param user_message: Messaggio corrente dell'utente
    :param retrieved_documents: Testo dei documenti rilevanti recuperati dal VectorStore
    :param history: Cronologia conversazionale precedente
    :return: Lista di tuple (ruolo, contenuto)
    """

    context_messages = []

    # Prompt di sistema
    context_messages.append(('system', ModelConfig.BASE_SYSTEM_PROMPT.strip()))

    # Prompt RAG
    if retrieved_documents:
        context_messages.append((
            'system',
            f"{ModelConfig.DOC_SYSTEM_TEMPLATE.strip()}\n{retrieved_documents}"
        ))

    # Aggiunge la cronologia limitata (per mantenere lo stato conversazionale)
    limited_history = history[-ChatConfig.CHAT_HISTORY_LIMIT:]
    context_messages.extend(limited_history)

    # Messaggio corrente dell'utente
    context_messages.append(('human', user_message))

    return context_messages


# http://127.0.0.1:9000/test
# Endpoint API: Chat con il modello
@app.route(WebConfig.APP_ROUTE_TEST, methods=['POST'])
def chat():
    """
    Endpoint API per l'interazione con l'assistente AI.
    Attende un JSON con il campo 'message' e restituisce la risposta generata.

    Request JSON:
    {
        "message": "testo dell'utente"
    }

    Response JSON:
    {
        "user": "messaggio dell'utente",
        "response": "risposta del modello AI"
    }

    :return: JSON con risposta o errore e codice HTTP
    """

    try:
        # Recupera i dati JSON dalla richiesta POST
        data = request.get_json()
        if not data: return jsonify({"error": "Richiesta non valida, JSON mancante"}), 400

        # Estrae e pulisce il messaggio dell'utente
        user_message = data.get("message", "").strip()
        if not user_message: return jsonify({"error": "Messaggio mancante"}), 400

        # Recupero del contesto dai documenti tramite retriever (RAG)
        documents = retriever.invoke(user_message)
        doc_text = "\n".join(doc.page_content for doc in documents)

        # Costruzione del contesto completo per il modello
        context = create_context(user_message, doc_text, chat_history)

        # Invocazione del modello AI
        response = model.invoke(context)
        ai_message = format_response(getattr(response, "content", str(response)).strip())

        # Aggiornamento cronologia conversazionale
        chat_history.append(('human', user_message))
        chat_history.append(('assistant', ai_message))

        # Restituisce la risposta in formato JSON
        return jsonify({
            "user": user_message,
            "response": ai_message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# http://127.0.0.1:9000/
# Endpoint per GUI frontend
@app.route('/', methods=['GET'])
def gui():
    """
    Restituisce l'interfaccia grafica (frontend statico).
    """
    return send_from_directory(WebConfig.STATIC_FOLDER, 'index.html')


# .\aicompanion\Scripts\activate
# cd .\aicompanion\
# python aicompanion.py

# conda activate aicuda
# cd Desktop\AIcompanion
# python aicompanion.py

if __name__ == '__main__':
    app.run(host=WebConfig.HOST, port=WebConfig.PORT, debug=WebConfig.DEBUG)

