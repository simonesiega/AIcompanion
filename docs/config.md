# Configurazione del sistema (`core/config.py`)

Il file **[core/config.py](../core/config.py)** contiene tutte le impostazioni principali utilizzate da AIcompanion. Ogni sezione è organizzata in classi.

Questi parametri influenzano il comportamento dei modelli linguistici, dei sistemi audio, del server Flask e della modalità interrogazione.

---

## ModelConfig
Configurazione del modello linguistico utilizzato tramite **Ollama**.

- **NAME** – nome del modello (es. `gemma3:4b`, `gemma3:12b`)
- **TEMPERATURE** – controlla la creatività (0 = deterministico)
- **REASONING** – abilita la modalità reasoning se supportata
- **BASE_SYSTEM_PROMPT** – prompt principale dell’assistente
- **DOC_SYSTEM_TEMPLATE** – template per risposte basate sui documenti RAG

Utilizzato:
- Chat principale  
- Modalità interrogazione  
- Pipeline RAG

## EmbeddingConfig
Controllo dei parametri per embeddings e chunking, utilizzati nella costruzione del **Vector Store**.

- **NAME** – modello di embedding (es. `embeddinggemma:300m`)
- **CHUNK_SIZE** – dimensione dei chunk di testo
- **CHUNK_OVERLAP** – sovrapposizione tra chunk
- **LENGTH_FUNCTION** – funzione per misurare la lunghezza del testo
- **IS_SEPARATOR_REGEX** – specifica se il separatore è una regex

Utilizzato:
- Creazione del vector store  
- Modulo RAG

## ChatConfig
Impostazioni della memoria conversazionale.

- **CHAT_HISTORY_LIMIT** – massimo numero di messaggi conservati

Utilizzato:
- Chat testuale  
- Chat vocale  

##  WebConfig
Configurazione del server Flask, cartelle statiche ed endpoint API.

- **STATIC_FOLDER** – nome cartella frontend della chat principale
- **STATIC_FOLDER_TEST** – nome cartella frontend modalità interrogazione
- **APP_ROUTE_TEST** – endpoint per messaggi testuali `/test`
- **APP_ROUTE_AUDIO** – endpoint per messaggi audio `/audio`
- **APP_ROUTE_INTERROGAZIONE_START** – avvio interrogazione
- **APP_ROUTE_INTERROGAZIONE_ANSWER** – risposta durante interrogazione
- **HOST / PORT** – configurazione server
- **DEBUG** – modalità debug

Utilizzato da:
- `aicompanion.py`  
- `aicompanion_test.py`

##  BenchmarksConfig
Configurazione dell sistema di benchmark CPU.

- **RUNS** – numero di snapshot ogni benchmark
- **SLEEP_TIME** – pausa tra snapshot
- **EXCEL_FILE** – nome del file Excel generato

Utilizzato da:
- `benchmarks/benchmark_loader.py`

##  KokoroConfig
Configurazione del sistema **Text-to-Speech (TTS) Kokoro**.

Include percorsi per modelli, configurazioni e voci.

- **MODEL_PATH**, **CONFIG_PATH** – posizione modelli
- **VOICES_PATH**, **VOICE_PATH** – voci disponibili
- **GENERATED_PATH** – cartella output audio
- **AUDIO_SPEED** – velocità voce sintetizzata
- **AUDIO_FREQ** – frequenza audio

Utilizzato da:
- Generazione risposte vocali
- Modalità chat vocale

##  WhisperConfig
Configurazione del modello **Whisper** (Speech-to-Text).

- **MODEL_PATH** – percorso del modello
- **DEVICE_NAME** – esecuzione su CPU o CUDA
- **LANGUAGE** – lingua della trascrizione

Utilizzato da:
- Endpoint `/audio`
- Pipeline ASR

##  TestChatConfig
Configurazione per la **modalità interrogazione**.

- **MODEL_NAME** – modello usato per spiegazioni e valutazioni
- **INTERROGATION_DIR** – cartella con file di test
- **CONTEXT_PATH** – file del contesto
- **QUESTIONS_PATH** – file delle domande
- **N_QUESTIONS** – numero di domande generate
- **get_db_paths()** – recupera tutti i DB presenti in `vs/`

Utilizzato da:
- `aicompanion_test.py`
- Sistema di valutazione quiz
- Vector store interrogazione