# Lib/site-packages
from flask import Flask, request, jsonify, send_file, send_from_directory
from langchain_ollama import ChatOllama

# .py
from config import MODEL_CONFIG
from utils import format_response


app = Flask(__name__, static_folder='static')

# Init modello
model = ChatOllama(
    model=MODEL_CONFIG.NAME,
    temperature=MODEL_CONFIG.TEMPERATURE,
    reasoning=MODEL_CONFIG.REASONING
)


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


        # Context per il modello
        # system, Ruolo del sistema
        # human, Messaggio dell'utente
        context = [
            ("system", "Sei un agente AI."),
            ("human", user_message)
        ]


        # Invia il contesto al modello e ottiene la risposta
        response = model.invoke(context)
        # La risposta è un oggetto LangChain
        # Estrae solo il contenuto testuale (elimina metriche)
        ai_message = format_response(getattr(response, "content", str(response)).strip())


        # Restituisce la risposta in formato JSON
        return jsonify({
            "user": user_message,
            "response": ai_message
        })


    # Gestione di errori durante il processo
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

