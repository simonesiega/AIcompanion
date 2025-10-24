"""
config.py
---------
Modulo di configurazione centrale.
Definisce costanti e parametri utilizzati da tutto il sistema.
"""

class ModelConfig:
    """
    Configurazione del modello linguistico utilizzato da Ollama.
    Tutti i parametri qui definiti devono essere considerati immutabili
    e validi per l'intera esecuzione del sistema.
    """
    # Nome del modello AI da utilizzare (Ollama)
    NAME: str = "gemma3:4b"  
    # NAME: str = "gemma3:12b"  
    TEMPERATURE: float = 0.1  # Controlla la creatività: 0 = deterministico
    REASONING: bool = False  # Flag per attivare modalità reasoning (se supportata dal modello)

    # Prompt di sistema principale (ruolo dell'assistente)
    BASE_SYSTEM_PROMPT: str = (
        "Sei Lewis Carroll, autore visionario. Rispondi con tono narrativo e poetico "
        "ma in modo chiaro e utile per l'utente moderno. Se non disponi di informazioni "
        "sufficienti dai documenti forniti, dichiara esplicitamente: 'Non trovo questa "
        "informazione nei miei scritti'. Usa un linguaggio elegante ma comprensibile."
    )

    # Template usato per integrare i documenti recuperati
    DOC_SYSTEM_TEMPLATE: str = (
        "Le seguenti informazioni provengono dai miei manoscritti e fonti verificate. "
        "Usa SOLO queste informazioni per rispondere. Se il contenuto non è rilevante "
        "per la domanda, ignoralo. Se non trovi la risposta, dì che non lo sai."
    )

class EmbeddingConfig:
    """
    Configurazione del modello di embedding e dei parametri di chunking.
    Utilizzata durante la fase di costruzione del Vector Store.
    """
    NAME: str = "embeddinggemma:300m"  # Nome del modello di embedding
    CHUNK_SIZE: int = 1000  # Dimensione di ogni chunk di testo
    CHUNK_OVERLAP: int = 500  # Numero di caratteri condivisi tra chunk consecutivi
    LENGTH_FUNCTION: str = len  # Funzione per calcolare la lunghezza del testo
    IS_SEPARATOR_REGEX: bool = False  # Specifica se il separatore è un'espressione regolare

class ChatConfig:
    """
    Configurazione del contesto conversazionale.
    """
    CHAT_HISTORY_LIMIT: int = 6  # Numero massimo di messaggi da mantenere in memoria

class WebConfig:
    """
    Configurazione del servizio web Flask.
    """
    STATIC_FOLDER: str = "static"  # Cartella per file frontend (HTML, CSS, JS)
    APP_ROUTE_TEST: str = "/test"  # Endpoint API principale
    HOST: str = "127.0.0.1"  # Host locale
    PORT: int = 9000  # Porta di esecuzione dell'app Flask
    DEBUG: bool = False
