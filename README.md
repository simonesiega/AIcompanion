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

Per una panoramica completa delle schermate dell’applicazione, consulta:

**[Tutti gli screenshot](./docs/screenshots.md)**

## Struttura del progetto

- Mappa completa delle cartelle (incluse quelle non presenti su GitHub):  
  **[struttura.md](./docs/struttura.md)**  
- Documentazione completa della configurazione (modelli, server, TTS, ASR, interrogazione):  
  **[config.md](./docs/config.md)**

La root del progetto è:

```
AIcompanion/
```

## Prerequisiti

- **Python 3.13** (versione consigliata per questo progetto)  
AIcompanion offre **piena compatibilità con tutte le librerie presenti nel progetto** solo utilizzando Python 3.13.  Versioni precedenti (< 3.13) non sono supportate: in particolare la libreria **audioop-lts**, necessaria per l’elaborazione audio, *non funziona* su versioni precedenti di Python.
- **ffmpeg** installato nel sistema (necessario per Whisper e Pydub)  
- Alcune librerie come *phonemizer* richiedono anche **espeak** o **espeak-ng**

### Nota su PyTorch
Nel file [requirements.txt ](./requirements.txt)sono presenti le dipendenze Torch commentate. Al momento PyTorch non distribuisce ancora una build stabile per **Python 3.13 + CUDA**.  
Quando sarà disponibile basterà decommentare:
- torch
- torchvision
- torchaudio

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
