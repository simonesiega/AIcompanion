"""
aicompanion_test.py
-------------------
Modalità "interrogazione" integrata in Flask.
Gestisce sessioni di domande/risposte valutate automaticamente.
"""

# Libreria standard per gestire percorsi e file system
import os

# Libreria per leggere e scrivere file JSON (contesto e domande)
import json

# Import principali per la creazione del server Flask e gestione richieste HTTP
from flask import Flask, request, jsonify, send_from_directory

# Modello linguistico
from langchain_ollama import ChatOllama

from core.config import (
    WebConfig,       # Impostazioni server Flask
    TestChatConfig   # Parametri interrogazione 
)

def load_interrogazione():
    """
    Carica il contesto e le domande per la modalità 'interrogazione'

    Restituisce:
        contesto (dict): contiene chiave "topic" e "content" con informazioni generali
        domande (dict): contiene chiave "topic" e lista "questions" con tutte le domande
    """

    # Verifica se i file JSON esistono, altrimenti solleva eccezione
    if not os.path.exists(TestChatConfig.CONTESTO_PATH) or not os.path.exists(TestChatConfig.DOMANDE_PATH):
        raise FileNotFoundError(
            "File contesto.json o domande.json mancanti nella cartella 'interrogazione/'"
        )

    # Carica il file contesto.json
    with open(TestChatConfig.CONTESTO_PATH, "r", encoding="utf-8") as f:
        contesto = json.load(f)

    # Carica il file domande.json
    with open(TestChatConfig.DOMANDE_PATH, "r", encoding="utf-8") as f:
        domande = json.load(f)

    # Restituisce entrambi i dizionari
    return contesto, domande

def valuta_risposta(domanda: str, risposta: str, lcmodel, context: list):
    """
    Valuta automaticamente la risposta di uno studente usando il modello AI.

    La funzione invia al modello AI il prompt contenente la domanda e la risposta
    dello studente, chiedendo una valutazione nel formato:
        [CORRETTA o SBAGLIATA]
        Breve spiegazione del perché è giusta o sbagliata.

    Parametri:
        domanda (str): La domanda a cui rispondere
        risposta (str): La risposta fornita dallo studente
        lcmodel (ChatOllama): Modello AI utilizzato per la valutazione
        context (list): Lista di tuple contenente il contesto della conversazione,
                        tipicamente [('system', ...), ('human', ...), ...]

    Restituisce:
        dict: {
            "valutazione": "CORRETTA" / "SBAGLIATA" / "ERRORE",
            "spiegazione": spiegazione dettagliata o messaggio di errore
        }
    """

    # Costruisce il prompt inviato al modello AI
    prompt = (
        f"Domanda: {domanda}\n"
        f"Risposta dello studente: {risposta}\n"
        "Valuta se la risposta è corretta nel seguente formato:\n"
        "[CORRETTA o SBAGLIATA]\n"
        "Breve spiegazione del perché è giusta o sbagliata."
    )

    # Copia il contesto esistente e aggiunge il prompt dell'utente
    local_context = context.copy()
    local_context.append(('human', prompt))

    try:
        # Invoca il modello AI con il contesto completo
        response = lcmodel.invoke(local_context)
        feedback = response.content.strip()

        # Divide il feedback in valutazione (prima riga) e spiegazione (resto)
        lines = feedback.split('\n', 1)
        valutazione = lines[0].strip('[] \n')  
        spiegazione = lines[1].strip() if len(lines) > 1 else ""  

        # Restituisce un dizionario con valutazione e spiegazione
        return {"valutazione": valutazione, "spiegazione": spiegazione}

    except Exception as e:
        # Gestione errori: restituisce stato ERRORE con descrizione
        return {"valutazione": "ERRORE", "spiegazione": str(e)}

class AICompanionTest:
    """
    Server Flask per la modalità 'interrogazione'.

    Questa classe gestisce un ciclo di domande/risposte valutate automaticamente 
    utilizzando un modello AI (ChatOllama).
    """

    def __init__(self):
        """Costruttore: inizializza tutti i moduli principali e registra le route Flask."""

        # Crea app Flask
        self.app = Flask(__name__, static_folder=WebConfig.STATIC_FOLDER_TEST)

        # Modello AI
        self.lcmodel = ChatOllama(model=TestChatConfig.MODEL_NAME)

        # Contesto iniziale di sistema per le valutazioni
        self.context = [("system", "Sei un professore che valuta risposte in modo oggettivo e chiaro.")]

        # Carica contesto e domande
        self.contesto, self.domande_data = load_interrogazione()
        self.domande = self.domande_data.get("questions", [])
        self.topic = self.domande_data.get("topic", "Argomento sconosciuto")

        # Sessione in memoria
        self.session_data = {
            "current_index": 0,
            "results": []
        }

        # Configura le rotte Flask
        self._register_routes()

    def _register_routes(self):
        """
        Registra tutte le route HTTP dell'applicazione Flask.

        Routes principali:
        - '/'           : Serve l'interfaccia utente HTML
        - '/start'      : Avvia l'interrogazione e restituisce la prima domanda
        - '/answer'     : Riceve la risposta dello studente, la valuta e restituisce la prossima domanda
        """

        @self.app.route('/', methods=['GET'])
        def gui():
            """
            Endpoint principale dell’interfaccia utente.
            Serve la pagina HTML statica `index_test.html`.

            Metodo: GET  
            """
            return send_from_directory(WebConfig.STATIC_FOLDER_TEST, 'index.html')

        @self.app.route(WebConfig.APP_ROUTE_INTERROGAZIONE_START, methods=['GET'])
        def start_test():
            """
            Endpoint per avviare l’interrogazione.

            Resetta la sessione corrente e restituisce la prima domanda
            insieme al contesto e alle informazioni sul numero totale di domande.

            Metodo: GET

            Returns:
                Response JSON con:
                    - topic (str): argomento dell'interrogazione
                    - contesto (str): contenuto del contesto
                    - domanda (str): prima domanda
                    - index (int): indice della domanda corrente (0)
                    - totale (int): numero totale di domande
                    - error (str, opzionale): messaggio di errore se non ci sono domande
            """

            # Verifica che ci siano domande disponibili
            if not self.domande:
                return jsonify({"error": "Nessuna domanda trovata."}), 400

            # Reset dello stato della sessione
            self.session_data["current_index"] = 0
            self.session_data["results"] = []

            # Recupera la prima domanda
            domanda = self.domande[0]

            # Restituisce la risposta JSON con prima domanda e info sessione
            return jsonify({
                "topic": self.topic,
                "contesto": self.contesto.get("content", ""),  
                "domanda": domanda,                            
                "index": 0,  # Indice domanda corrente
                "totale": len(self.domande)                  
            })

        @self.app.route(WebConfig.APP_ROUTE_INTERROGAZIONE_ANSWER, methods=['POST'])
        def answer_test():
            """
            Endpoint per ricevere la risposta dello studente e fornire feedback.

            Riceve una risposta, la valuta tramite il modello AI e aggiorna
            lo stato della sessione. Restituisce la prossima domanda se disponibile,
            altrimenti un riepilogo finale dell'interrogazione.

            Metodo: POST

            Request JSON:
                - risposta (str): risposta dello studente alla domanda corrente

            Response JSON:
                - valutazione (dict): {"valutazione": "CORRETTA/SBAGLIATA", "spiegazione": "..."}
                - next_domanda (str, opzionale): prossima domanda
                - index (int): indice della domanda corrente
                - totale (int): numero totale di domande
                - finished (bool): indica se l'interrogazione è terminata
                - risultati (list, opzionale): lista dei risultati per tutte le domande
                - corrette (int, opzionale): numero di risposte corrette totali
            """

            # Legge la risposta inviata dall'utente
            data = request.get_json(force=True)
            risposta = data.get("risposta", "")

            # Indice della domanda corrente nella sessione
            idx = self.session_data["current_index"]

            # Controlla se l'interrogazione è già terminata
            if idx >= len(self.domande):
                return jsonify({"finished": True, "message": "Interrogazione già terminata."})

            # Recupera la domanda corrente
            domanda = self.domande[idx]

            # Valuta la risposta tramite il modello AI
            valutazione = valuta_risposta(domanda, risposta, self.lcmodel, self.context)

            # Aggiorna lo stato della sessione con il risultato della valutazione
            self.session_data["results"].append(valutazione)
            self.session_data["current_index"] += 1

            # Se ci sono ancora domande, restituisce la prossima
            if self.session_data["current_index"] < len(self.domande):
                next_q = self.domande[self.session_data["current_index"]]
                return jsonify({
                    "valutazione": valutazione,
                    "next_domanda": next_q,
                    "index": self.session_data["current_index"],
                    "totale": len(self.domande),
                    "finished": False
                })
            
            else:
                # Tutte le domande sono state completate → riepilogo finale
                corrette = sum(1 for r in self.session_data["results"]
                            if r["valutazione"].upper().startswith("CORR"))
                return jsonify({
                    "valutazione": valutazione,
                    "finished": True,
                    "risultati": self.session_data["results"],
                    "corrette": corrette,
                    "totale": len(self.session_data["results"])
                })

    # Avvio server Flask
    def run(self):
        """
        Avvia l'applicazione Flask per il bot AI.

        Parametri:
            - host: indirizzo IP o hostname su cui il server ascolta (WebConfig.HOST)
            - port: porta del server (WebConfig.PORT)
            - debug: modalità debug attiva/disattiva (WebConfig.DEBUG)
        """
        self.app.run(
            host=WebConfig.HOST,
            port=WebConfig.PORT,
            debug=WebConfig.DEBUG
        )


if __name__ == "__main__":
    test_app = AICompanionTest()
    test_app.run()
