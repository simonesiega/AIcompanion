<h1 align="center">AIcompanion</h1>

<p align="center">
  <a href="https://github.com/simonesiega/AIcompanion/commits/main">
    <img alt="Last commit" src="https://img.shields.io/github/last-commit/simonesiega/AIcompanion" />
  </a>
  <a href="https://github.com/simonesiega/AIcompanion/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/simonesiega/AIcompanion" />
  </a>
  <a href="https://github.com/simonesiega/AIcompanion/stargazers">
    <img alt="Stars" src="https://img.shields.io/github/stars/simonesiega/AIcompanion" />
  </a>
  <a href="https://github.com/simonesiega/AIcompanion/network/members">
    <img alt="Forks" src="https://img.shields.io/github/forks/simonesiega/AIcompanion" />
  </a>
  <a href="https://github.com/simonesiega/AIcompanion/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/simonesiega/AIcompanion" />
  </a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB" />
  <img alt="Flask" src="https://img.shields.io/badge/Web-Flask-000000" />
  <img alt="Ollama" src="https://img.shields.io/badge/LLM-Ollama-111111" />
  <img alt="RAG" src="https://img.shields.io/badge/RAG-Vector%20Store-6A5ACD" />
  <img alt="Whisper" src="https://img.shields.io/badge/ASR-Whisper-2E8B57" />
  <img alt="Kokoro" src="https://img.shields.io/badge/TTS-Kokoro-8A2BE2" />
</p>

<p align="center">
  Assistente AI modulare (Python + Flask) con chat testuale e vocale, modalità di “interrogazione” con valutazione automatica, e ricerca semantica RAG.
</p>

<p align="center">
    <img src="https://github.com/user-attachments/assets/96f102b4-5998-489a-be3b-34fd545aee5d" width="700" alt="Presentation" />
</p>
<p align="center">
   AIcompanion nasce per unire conversazione naturale (testo/voce) e strumenti didattici (interrogazioni e feedback) in un’unica app locale e modulare.  
   L’obiettivo è avere un “compagno” che non solo risponde, ma può anche contestualizzare (RAG) e valutare.
</p>

## Funzionalità principali

- Chat testuale e vocale: input testo/audio, risposta LLM, salvataggio su disco (`questions/` e `responses/`).
- Pipeline voce end-to-end: Speech-to-Text con Whisper, Text-to-Speech con Kokoro.
- Modalità “interrogazione”: sessioni di test, valutazione automatica (CORRETTA/SBAGLIATA) con spiegazioni e riepilogo finale.
- Ricerca semantica (RAG): recupero documenti pertinenti tramite vector store + embeddings (OllamaEmbeddings).
- Modularità: componenti separati (ASR/TTS/RAG/valutazione) per estendere facilmente modelli e flussi.

## Scalabilitá

AIcompanion è progettato come piattaforma modulare dove:
- L’esperienza utente può alternare chat libera e sessioni strutturate di test.
- I modelli possono essere sostituiti/aggiornati senza riscrivere l’intera app (LLM, embeddings, ASR, TTS).
- Le risposte possono essere arricchite con conoscenza esterna tramite RAG per aumentare coerenza e utilità.

## Architettura & Tech Overview

| Area | Technology | Goal |
|---|---|---|
| App | Python + Flask | Web app semplice, estendibile, con endpoint per testo e audio |
| LLM | ChatOllama | Risposte conversazionali locali |
| ASR | Whisper (+ ffmpeg) | Trascrizione audio → testo |
| TTS | Kokoro | Sintesi vocale testo → audio |
| RAG | Vector Store + OllamaEmbeddings | Recupero contesto semantico per risposte più pertinenti |
| Storage | File system (`questions/`, `responses/`) | Persistenza semplice di domande/risposte |

## Screenshots & docs
<p align="center">
  <a href="screen/">
    <img 
      width="360"
      height="360"
      src="screen/chat.png" width="345" alt="Home page black theme" />
  </a>
  <a href="screen/">
    <img 
      width="360"
      height="360"
      src="screen/test.png" width="345" alt="Login white theme" />
  </a>
</p>

## Contributing & support 🤝

I contributi sono benvenuti.

- Per bug e feature request, apri una Issue
- Per contributi al codice, apri una **Pull Request** con una descrizione chiara della modifica e della motivazione
- Per contatti diretti, scrivimi a simonesiega1@gmail.com o contattami su GitHub

## License

Questo progetto è distribuito sotto i termini della licenza MIT, come indicato nel file LICENSE.

## Contributors 🧑‍💻

<p align="center">
<a href="https://github.com/simonesiega">
<img
src="https://github.com/simonesiega.png?size=160"
width="80"
height="80"
alt="simonesiega"
style="border-radius: 50%;"
/>
</a>
</p>
