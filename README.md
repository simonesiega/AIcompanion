# AIcompanion

AIcompanion è un assistente AI modulare basato su Python e Flask, progettato per fornire interazioni conversazionali testuali e vocali, con funzionalità di valutazione automatica delle risposte e integrazione di modelli linguistici.

---

## Funzionalità principali

1. **Chat testuale e vocale**
   - Riceve messaggi testuali o audio dall'utente
   - Utilizza **ChatOllama** per generare risposte coerenti
   - Supporto Text-to-Speech con **Kokoro**
   - Supporto Speech-to-Text con **Whisper**
   - Salvataggio di domande e risposte su disco (`questions/` e `responses/`)

2. **Modalità "interrogazione"**
   - Valuta automaticamente le risposte dello studente
   - Genera un feedback con valutazione **CORRETTA/SBAGLIATA** e spiegazioni
   - Gestione sessioni e riepilogo finale dei risultati

3. **Ricerca semantica RAG**
   - Integrazione con **Vector Store** e embeddings tramite **OllamaEmbeddings**
   - Recupero dei documenti più pertinenti per contestualizzare le risposte

4. **Modularità**
   - Pipeline audio separata per TTS
   - Pipeline per trascrizione vocale ASR
   - Facile estensione con nuovi modelli o moduli

## Screenshot

### [aicompanion.py](./aicompanion.py) - Chat Bot interattiva:
- Interfaccia principale utilizzata per la comunicazione con l’assistente AI, tramite messaggi testuali o audio.  
Consente dialoghi naturali e sfrutta i modelli TTS/ASR integrati.
  
![Chat Bot interattiva](screen/chat.png)

### [aicompanion_test.py](./aicompanion_test.py) - Chat Bot interrogazione:
- Schermata dedicata alle sessioni di test: lo studente risponde alle domande, e il sistema valuta automaticamente correttezza e spiegazione.
  
![Chat Bot interrogazione](screen/test.png)

## Struttura del progetto

- Mappa completa delle cartelle (incluse quelle non presenti su GitHub):  
  **[struttura.md](./docs/struttura.md)**  
- Documentazione completa della configurazione (modelli, server, TTS, ASR, interrogazione):  
  **[config.md](./docs/config.md)**

La root del progetto è:

```
AIcompanion/
```

## Installazione

### 1. Clona la repo:

```
git clone https://github.com/simonesiega/AIcompanion.git
```

### 2. Installa le dipendenze:
```
pip install -r requirements.txt
```

### 3. Struttura del progetto e modelli richiesti

La struttura completa delle cartelle (incluse quelle **non versionate**) e l’elenco dei modelli necessari sono descritti in:

- **[struttura.md](./docs/struttura.md)** → contiene cartelle, file e modelli da aggiungere manualmente  
- **[comandi.md](./docs/comandi.md)** → comandi utili per avvio, ambiente e debug

Assicurati di seguire le istruzioni riportate in questi due file prima di avviare l’applicazione.

## Avvio

### 1. Modalità Chat AI

```
python aicompanion.py
```
   - Interfaccia web principale
   - Invio messaggi testuali → endpoint **/test**
   - Invio messaggi audio → endpoint **/audio**


### 2. Modalità Interrogazione

```
python aicompanion_test.py
```
   - Interfaccia web dedicata al test
   - Avvio interrogazione → endpoint **/start**
   - Risposta a domande → endpoint **/answer**
