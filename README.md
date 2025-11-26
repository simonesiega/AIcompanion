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

---

## Struttura del progetto

Per la mappa completa delle cartelle, inclusi file e cartelle **non presenti su GitHub**, consultare il file **[struttura.md](./struttura.md)**.  

La root del progetto è `AIcompanion/`.

---

## Installazione

### 1. Clona la repo:

```
git clone https://github.com/simonesiega/AIcompanion.git
```

### 2. Installa le dipendenze:
```
pip install -r requirements.txt
```

3. Assicurati di avere le cartelle e i modelli non versionati come indicato in **[struttura.md](./struttura.md)**.

## Avvio

### 1. Modalità Chat AI

```
python aicompanion.py
```
   - Accedi all’interfaccia web
   - Invio messaggi testuali → endpoint **/test**
   - Invio messaggi audio → endpoint **/audio**


### 2. Modalità Interrogazione

```
python aicompanion_test.py
```
   - Accedi all’interfaccia web dedicata alla modalità test
   - Avvio interrogazione → endpoint **/start**
   - Risposta a domande → endpoint **/answer**
