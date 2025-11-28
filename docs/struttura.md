# Struttura del progetto AI Companion

## Introduzione

Questa pagina fornisce una **mappa delle cartelle non presenti su GitHub** all'interno del progetto AI Companion.  
La root del progetto è:

```
AIcompanion/
```

Ogni sezione descrive:
- Il **percorso completo** della cartella all'interno di `AIcompanion`
- Lo **scopo** della cartella
- I **file principali** contenuti
- Eventuali note su **dipendenze o uso speciale**

## 1. Kokoro

**Percorso:** `AIcompanion/kokoro`

**Scopo:** Contiene i moduli principali del progetto AI Kokoro e lo script eseguibile.

**Contenuto:**

| File | Scopo |
|------|-------|
| `custom_stft.py` | Funzioni custom per STFT |
| `istftnet.py` | Modulo principale rete ISTFT |
| `model.py` | Definizione dei modelli di rete neurale |
| `modules.py` | Moduli ausiliari utilizzati dai modelli |
| `pipeline.py` | Gestione pipeline di elaborazione e inferenza |
| `__init__.py` | Package Python |
| `__main__.py` | Script principale eseguibile |

## 2. Models

**Percorso:** `AIcompanion/models`

**Scopo:** Contiene i modelli pre-addestrati e relativi file di configurazione per il progetto.  
Include anche sottocartelle come `voices` che raggruppano modelli vocali specifici.

**Contenuto:**

| File/Cartella | Scopo |
|---------------|-------|
| `config.json` | Configurazione generale dei modelli. |
| `kokoro-v1_0.pth` | Modello principale Kokoro versione 1.0. |
| `small.pt` | Modello compatto di test o inferenza rapida. |
| `voices/` | Sottocartella contenente modelli vocali (`.pt`) specifici per ciascuna voce. |

**Esempio di file `.pt` in `voices/`:**

| File | Scopo |
|------|-------|
| `af_alloy.pt` | Modello vocale di esempio (voce femminile Alloy). |
| `am_adam.pt` | Modello vocale di esempio (voce maschile Adam). |
| `if_alpha.pt` | Modello vocale alternativo Alpha. |

