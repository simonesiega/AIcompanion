# Lib/site-packages
from flask import Flask, request, jsonify, send_file, send_from_directory
from langchain_ollama import ChatOllama


# .py
from config import MODEL_CONFIG
from utils import format_response


app = Flask(__name__, static_folder='static')


from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
embeddings = OllamaEmbeddings(
    model = "embeddinggemma:300m"
)
vs = InMemoryVectorStore.load("./vs/alice.db", embedding = embeddings)
retriever = vs.as_retriever()


# Init modello
model = ChatOllama(
    model=MODEL_CONFIG.NAME,
    temperature=MODEL_CONFIG.TEMPERATURE,
    reasoning=MODEL_CONFIG.REASONING
)


BASE_CONTEXT = [
    ('system', "Sei Lewis Carroll e stai raccontando il tuo libro con tono narrativo e poetico."),
]
chat_history = []


# http://127.0.0.1:9000/test
@app.route('/test', methods=['POST'])
def chat():
    """
    Endpoint POST per ricevere messaggi dall'utente e rispondere con il modello AI.


    Request JSON:
        {
            "message": "testo dell'utente"
        }


    Response JSON:
        {
            "user": "messaggio dell'utente",
            "response": "risposta del modello AI"
        }


    Return:
        tuple: JSON con risposta o errore e codice HTTP
    """
    try:
        # Recupera i dati JSON dalla richiesta POST
        data = request.get_json()
        if not data: return jsonify({"error": "Richiesta non valida, JSON mancante"}), 400


        # Estrae e pulisce il messaggio dell'utente
        user_message = data.get("message", "").strip()
        if not user_message: return jsonify({"error": "Messaggio mancante"}), 400


        documents = retriever.invoke(user_message)
        doc_text = "\n".join(doc.page_content for doc in documents)


        context = create_context(user_message, doc_text, chat_history)


        response = model.invoke(context)
        ai_message = format_response(getattr(response, "content", str(response)).strip())


        # Salva la risposta nella memoria chat
        chat_history.append(('human', user_message))
        chat_history.append(('assistant', ai_message))


        # Restituisce la risposta in formato JSON
        return jsonify({
            "user": user_message,
            "response": ai_message
        })


    # Gestione di errori durante il processo
    except Exception as e:
        return jsonify({"error": str(e)}), 500




def create_context(user_message: str, doc_context: str, chat_history: list):
    """
    Crea un contesto ordinato da passare al modello seguendo:
    system → system (document context) → messaggi alternati utente/assistente
    system → user → assistant → user → assistant
    """
    context = BASE_CONTEXT.copy()


    # Inserisce il contesto dei documenti come secondo system
    context.append((
        'system', "Rispondi usando SOLO le informazioni qui sotto. Se non trovi la risposta, dì che non lo sai.\n" + doc_context
    ))


    # Aggiorna la cronologia della chat
    # chat_history è una lista di tuple: ('human', msg) o ('assistant', msg)
    for role, message in chat_history:
        context.append((role, message))


    # Aggiunge il messaggio corrente dell'utente
    context.append(('human', user_message))


    return context


# http://127.0.0.1:9000/
@app.route('/', methods=['GET'])
def gui():
    """
    Endpoint principale della web app
    Ritorna file index.html dalla cartella web.


    Return:
        str: Contenuto del file HTML o messaggio di errore se non trovato
    """
    return send_from_directory('static', 'index.html')


# .\aicompanion\Scripts\activate
# cd .\aicompanion\
# python aicompanion.py
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=9000, debug=False)

