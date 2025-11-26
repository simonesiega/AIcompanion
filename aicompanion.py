"""
aicompanion.py
---------------
Modulo principale del backend Flask.
Gestisce la comunicazione tra frontend e modello AI
"""

# Import principali per la creazione del server Flask e gestione richieste HTTP
from flask import Flask, request, jsonify, send_from_directory

# Modelli linguistici e embedding tramite LangChain + Ollama
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Vector Store in memoria per salvataggio temporaneo degli embedding
from langchain_community.vectorstores import InMemoryVectorStore

from core.config import (
    ModelConfig,       # Parametri del modello di chat Ollama
    EmbeddingConfig,   # Parametri del modello di embedding
    ChatConfig,        # Parametri di sessione chat
    WebConfig,         # Impostazioni server Flask
    KokoroConfig,      # Parametri per la voce sintetica (TTS)
    WhisperConfig      # Parametri per il modello di trascrizione audio (ASR)
)

# Formattazione per HTML e TTS
from core.utils import format_for_html, format_for_tts

# Embedding e creazione .db vettoriali
from core.vector_utils import load_DB, get_relevant_chunks

# Libreria PyTorch
import torch

# Gestione di stringhe binarie e codifica base64
import base64

# Lettura/scrittura di file audio
import soundfile as sf

# Moduli principali di Kokoro
from kokoro import KPipeline, KModel

# Whisper per la trascrizione vocale (speech-to-text)
import whisper

# Pydub per conversione e manipolazione di file audio
from pydub import AudioSegment

# Libreria standard per gestire flussi binari in memoria
import io

# Libreria standard per gestire percorsi e file system
import os


class AICompanion:
    def __init__(self):
        """Costruttore: inizializza tutti i moduli principali e registra le route Flask."""

        # SEZIONE DISPOSITIVO
        # Se CUDA è disponibile, usa la GPU, altrimenti la CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Dispositivo scelto per il modello: {self.device}")

        # SEZIONE FLASK
        # Crea l'app Flask, specificando la cartella dei file statici (frontend)
        self.app = Flask(__name__, static_folder=WebConfig.STATIC_FOLDER)

        # SEZIONE MODELLO DI CHAT
        # Inizializza il modello linguistico Ollama con i parametri da config
        self.model = ChatOllama(
            model=ModelConfig.NAME, # Nome modello 
            temperature=ModelConfig.TEMPERATURE, # Controlla la creatività delle risposte
            reasoning=ModelConfig.REASONING, # Abilita eventuali capacità di ragionamento
            device=self.device # Esegue su GPU se disponibile
        )

        # SEZIONE EMBEDDINGS & VECTOR STORE
        # Generatore di embeddings basato su Ollama
        self.embeddings = OllamaEmbeddings(model=EmbeddingConfig.NAME)

        # Carica e unisce tutti i database vettoriali presenti in ./vs
        # Ogni .db contiene embedding di documenti diversi utilizzati per la ricerca semantica (RAG)
        self.vs = load_DB()

        # Crea un retriever dal Vector Store per effettuare ricerche semantiche (RAG)
        # Il retriever permette di recuperare i documenti più rilevanti rispetto a una domanda utente.
        self.retriever = self.vs.as_retriever()

        # SEZIONE CRONOLOGIA CHAT
        # Mantiene lo storico delle conversazioni (prompt e risposte)
        self.chat_history = []

        # SEZIONE MODELLO AUDIO - TTS (KOKORO)
        # Inizializza il modello vocale di Kokoro e lo porta su CPU
        self.kmodel = KModel(
            model=KokoroConfig.MODEL_PATH, # Percorso al file del modello TTS
            config=KokoroConfig.CONFIG_PATH # Percorso al file di configurazione
        ).to("cpu")

        # Pipeline di sintesi vocale (Text-to-Speech)
        self.pipeline = KPipeline(
            lang_code="i", # Codice lingua ("i" per italiano)
            model=self.kmodel
        )

        # SEZIONE MODELLO AUDIO - ASR (WHISPER)
        # Carica il modello Whisper per la trascrizione audio → testo
        self.wmodel = whisper.load_model(
            name=WhisperConfig.MODEL_PATH, # Nome o percorso del modello Whisper
            device=WhisperConfig.DEVICE_NAME # Dispositivo su cui caricare il modello
        )

        # SEZIONE SALVATAGGIO
        # Salvataggio su disco (storico domande/risposte)
        os.makedirs("questions", exist_ok=True)
        os.makedirs("responses", exist_ok=True)

        # SEZIONE ROUTE FLASK
        # Registra tutte le route API (es. /test, /audio, /static ecc.)
        self._register_routes()

    def create_context(self, user_message: str, retrieved_documents: str):
        """
        Crea il contesto completo da fornire al modello di chat.

        Parametri:
            user_message (str): Messaggio inviato dall'utente.
            retrieved_documents (str): Testo concatenato dei documenti recuperati dal VectorStore.

        Restituisce:
            list[tuple[str, str]]: Lista di coppie (ruolo, messaggio) da passare al modello.
                                   Include:
                                   - Prompt di sistema base
                                   - Eventuali documenti di contesto
                                   - Cronologia conversazionale recente
                                   - Ultimo messaggio utente
        """

        # Prompt di sistema iniziale, definito in config
        context_messages = [('system', ModelConfig.BASE_SYSTEM_PROMPT.strip())]

        # Se sono stati recuperati documenti dal Vector Store, li aggiunge al contesto
        if retrieved_documents:
            context_messages.append((
                'system',
                f"{ModelConfig.DOC_SYSTEM_TEMPLATE.strip()}\n{retrieved_documents}"
            ))

        # Limita la cronologia alle ultime N interazioni 
        limited_history = self.chat_history[-ChatConfig.CHAT_HISTORY_LIMIT:]

        # Aggiunge la cronologia al contesto
        context_messages.extend(limited_history)

        # Inserisce il messaggio corrente dell’utente
        context_messages.append(('human', user_message))

        # Ritorna il contesto completo (system + documents + history + user)
        return context_messages

    def chat_text(self, user_message):
        """
        Gestisce una singola interazione testuale con l'assistente AI.

        Passaggi:
        1. Recupera documenti semantici pertinenti tramite il retriever.
        2. Costruisce il contesto con documenti + cronologia + messaggio utente.
        3. Invoca il modello linguistico (ChatOllama) con il contesto.
        4. Restituisce la risposta formattata per HTML e TTS.

        Parametri:
            user_message (str): Messaggio inviato dall'utente.

        Restituisce:
            tuple[str, str]:
                - ai_message_html → Risposta formattata per l’interfaccia web.
                - ai_message_tts → Risposta pulita per la sintesi vocale (TTS).
        """

        # Recupera documenti rilevanti 
        documents = self.retriever.invoke(user_message)

        # Concatena il contenuto testuale dei documenti trovati
        doc_text = "\n".join(doc.page_content for doc in documents)

        # Combina prompt di sistema, documenti, cronologia e messaggio utente
        context = self.create_context(user_message, doc_text)

        # Esegue la chiamata al modello Ollama con il contesto completo
        response = self.model.invoke(context)

        # Estrae la risposta testuale grezza 
        ai_message_raw = getattr(response, "content", str(response)).strip()

        # Converte la risposta per output HTML 
        ai_message_html = format_for_html(ai_message_raw)
        # Converte la risposta per sintesi vocale
        ai_message_tts = format_for_tts(ai_message_raw)

        # Aggiunge il messaggio utente e la risposta AI alla cronologia
        self.chat_history.append(('human', user_message))
        self.chat_history.append(('assistant', ai_message_html))

        # Restituisce la risposta HTML per la chat e la versione TTS per eventuale voce
        return ai_message_html, ai_message_tts

    def text_to_speech(self, text):
            """
            Converte un testo in parlato (audio WAV) utilizzando il modello Kokoro.

            Passaggi:
            1. Esegue la pipeline TTS (Text-To-Speech) con la voce e velocità configurate.
            2. Salva ciascun frammento audio generato su disco.
            3. Restituisce i percorsi dei file audio generati.

            Parametri:
                text (str): Testo da convertire in parlato.

            Restituisce:
                list[str]: Elenco dei percorsi ai file WAV generati.
            """

            # Esegue la pipeline di generazione vocale Kokoro
            generator = self.pipeline(
                text,
                voice=KokoroConfig.VOICE_PATH,    
                speed=KokoroConfig.AUDIO_SPEED    
            )

            # Lista dei file WAV generati
            audio_paths = []  

            # Ogni ciclo restituisce: (timestamp_inizio, timestamp_fine, array_audio)
            for i, (_, _, audio) in enumerate(generator):
                # Costruisce il percorso di output per ciascun file
                path = f"{KokoroConfig.GENERATED_PATH}{i}.wav"

                # Scrive l’audio su disco in formato WAV 16-bit PCM
                sf.write(path, audio, KokoroConfig.AUDIO_FREQ, "PCM_16")

                # Salva il percorso nella lista di output
                audio_paths.append(path)

            # Restituisce la lista completa dei file generati
            return audio_paths

    def speech_to_text(self, audio_path):
        """
        Converte un file audio in testo utilizzando il modello Whisper.

        Passaggi:
        1. Esegue la trascrizione automatica del parlato (Speech-to-Text).
        2. Specifica lingua e precisione FP32 per compatibilità.
        3. Restituisce la trascrizione testuale pulita.

        Parametri:
            audio_path (str): Percorso del file audio da trascrivere.

        Restituisce:
            str: Testo trascritto dal parlato.
        """

        # Esegue la trascrizione con il modello Whisper
        result = self.wmodel.transcribe(
            audio=audio_path,
            language=WhisperConfig.LANGUAGE,  
            fp16=False                   
        )

        # Restituisce solo il campo 'text' se il risultato è un dizionario
        return result.get('text') if isinstance(result, dict) else str(result)

    # ROUTES Flask
    def _register_routes(self):
        """
        Registra tutte le route HTTP dell'applicazione Flask.

        Ogni route collega un endpoint frontend o API a una specifica funzione
        di gestione lato server (controller).

        Routes principali:
        - `/` : Serve l’interfaccia grafica principale (index.html)
        - `/test` : Gestisce i messaggi testuali utente → AI
        - `/audio` : Gestisce i messaggi vocali (Speech-to-Text + risposta AI)
        """

        @self.app.route('/', methods=['GET'])
        def gui():
            """
            Endpoint principale dell’interfaccia utente.
            Serve la pagina HTML statica `index.html` contenuta nella cartella
            definita in `WebConfig.STATIC_FOLDER`.

            Metodo: GET  
            Utilizzo: Carica l’interfaccia frontend della chat AI nel browser.
            """
            # Restituisce il file index.html dalla directory statica configurata
            return send_from_directory(WebConfig.STATIC_FOLDER, 'index.html')

        # Route: /test 
        @self.app.route(WebConfig.APP_ROUTE_TEST, methods=['POST'])
        def chat():
            """
            Gestisce una richiesta di chat testuale (POST).

            Funzionamento:
            1. Riceve dal frontend un messaggio utente in formato JSON.
            2. Elabora il messaggio tramite il modello LLM (`ChatOllama`).
            3. Salva la domanda e la risposta su disco (per logging/debug).
            4. Se richiesto, genera anche l’audio della risposta (TTS con Kokoro).
            5. Restituisce un oggetto JSON con il testo (e l’audio opzionale in Base64).

            Endpoint configurato in: `WebConfig.APP_ROUTE_TEST`
            Metodo: POST
            Parametri JSON:
                - "message": testo del messaggio utente
            Parametri opzionali (query string):
                - "tts": "1" per generare anche l’audio della risposta (default: "0")

            Risposta JSON:
                {
                    "user": "<testo utente>",
                    "response": "<risposta AI pulita>",
                    "base64": "<audio codificato Base64, se richiesto>"
                }
            """
            try:
                # Lettura e validazione input
                data = request.get_json()
                if not data or not data.get("message"):
                    return jsonify({"error": "Messaggio mancante"}), 400

                # Normalizza il messaggio utente
                user_message = data["message"].strip()

                # Genera la risposta del modello AI
                ai_message_html, ai_message_tts = self.chat_text(user_message)

                # Trova il prossimo indice disponibile (1, 2, 3, ...)
                idx = 1
                while os.path.exists(os.path.join("questions", f"{idx}.txt")):
                    idx += 1

                # Salva la domanda
                with open(os.path.join("questions", f"{idx}.txt"), "w", encoding="utf-8") as f:
                    f.write(user_message)

                # Salva la risposta (versione pulita per TTS)
                with open(os.path.join("responses", f"{idx}.txt"), "w", encoding="utf-8") as f:
                    f.write(ai_message_tts)

                # Generazione audio opzionale (TTS)
                generate_audio = request.args.get("tts", "0") == "1"
                base64_audio = None

                if generate_audio:
                    # Genera i segmenti audio tramite Kokoro
                    audio_paths = self.text_to_speech(ai_message_tts)

                    # Combina eventuali più segmenti audio in un unico file
                    combined = AudioSegment.from_wav(audio_paths[0])
                    for path in audio_paths[1:]:
                        combined += AudioSegment.from_wav(path)

                    # Esporta l’audio combinato e codifica in Base64
                    output_path = os.path.join("responses", f"{idx}.wav")
                    combined.export(output_path, format="wav")
                    with open(output_path, "rb") as f:
                        base64_audio = base64.b64encode(f.read()).decode("utf-8")

                # Risposta finale al client
                resp = {
                    "user": user_message,
                    "response": ai_message_tts,
                }
                if base64_audio:
                    resp["base64"] = base64_audio

                return jsonify(resp)

            except Exception as e:
                # Gestione di eventuali errori imprevisti
                return jsonify({"error": str(e)}), 500


        # Route: /audio 
        @self.app.route(WebConfig.APP_ROUTE_AUDIO, methods=['POST'])
        def chataudio():
            """
            Gestisce una richiesta di chat tramite audio (POST).

            Funzionamento:
            1. Riceve un file audio dall'utente nel body della richiesta.
            2. Salva l'audio su disco per logging.
            3. Trascrive l'audio in testo tramite Whisper.
            4. Genera la risposta del modello AI (`ChatOllama`).
            5. Salva la trascrizione e la risposta su disco.
            6. Se richiesto, genera anche l’audio della risposta (TTS con Kokoro).
            7. Restituisce JSON con trascrizione, risposta testuale e audio opzionale.

            Endpoint configurato in: `WebConfig.APP_ROUTE_AUDIO`
            Metodo: POST
            Parametri opzionali (query string):
                - "tts": "1" per generare anche l’audio della risposta (default: "0")

            Risposta JSON:
                {
                    "user": "<trascrizione audio utente>",
                    "response": "<risposta AI pulita>",
                    "base64": "<audio codificato Base64, se richiesto>"
                }
            """
            try:
                # Lettura del body audio
                audio_bytes = request.get_data()
                if not audio_bytes:
                    return jsonify({"error": "Body audio mancante"}), 400

                # Determina prossimo indice disponibile
                idx = 1
                while os.path.exists(os.path.join("questions", f"{idx}.wav")):
                    idx += 1

                # Salva audio utente su disco
                user_path = os.path.join("questions", f"{idx}.wav")
                with open(user_path, 'wb') as f:
                    f.write(audio_bytes)

                # Trascrizione dell’audio utente
                user_message = self.speech_to_text(user_path)

                # Salva la trascrizione testuale
                with open(os.path.join("questions", f"{idx}.txt"), "w", encoding="utf-8") as f:
                    f.write(user_message)

                # Generazione risposta AI
                ai_message_html, ai_message_tts = self.chat_text(user_message)

                # Salva la risposta testuale pulita
                with open(os.path.join("responses", f"{idx}.txt"), "w", encoding="utf-8") as f:
                    f.write(ai_message_tts)

                # Generazione audio TTS opzionale
                generate_audio = request.args.get("tts", "0") == "1"
                base64_audio = None

                if generate_audio:
                    # Genera segmenti audio tramite Kokoro
                    audio_paths = self.text_to_speech(ai_message_tts)

                    # Combina eventuali segmenti multipli in un unico file WAV
                    combined = AudioSegment.from_wav(audio_paths[0])
                    for path in audio_paths[1:]:
                        combined += AudioSegment.from_wav(path)

                    # Esporta l’audio combinato e codifica in Base64
                    output_path = os.path.join("responses", f"{idx}.wav")
                    combined.export(output_path, format="wav")
                    with open(output_path, "rb") as f:
                        base64_audio = base64.b64encode(f.read()).decode("utf-8")

                # Prepara e invia risposta JSON
                resp = {
                    "user": user_message,
                    "response": ai_message_tts,
                }
                if base64_audio:
                    resp["base64"] = base64_audio

                return jsonify(resp)

            except Exception as e:
                # Gestione errori generici
                return jsonify({"error": str(e)}), 500

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
    companion = AICompanion()
    companion.run()