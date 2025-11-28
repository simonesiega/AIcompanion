# Screenshot – AIcompanion

Questa pagina raccoglie e descrive tutte le principali schermate dell’interfaccia utente di **AIcompanion**, incluse la modalità **Chat** e la modalità **Interrogazione**.  
Le immagini provengono dall’interfaccia web basata su Flask, ottimizzata per l’utilizzo da desktop.

### aicompanion.py - Interfaccia Chat:
File: **[aicompanion.py](../aicompanion.py)**

Questa è l’interfaccia principale per interagire con l’assistente AI, tramite messaggi **testuali** o **vocali**.

Funzionalità:
- Area chat
- Input testuale
- Pulsante microfono per registrare audio
- Risposte vocali tramite **TTS (Kokoro)**
- Integrazione **ASR (Whisper)**

![Screenshot Chat interattiva](../screen/chat.png)


### aicompanion_test.py - Modalità Interrogazione:
File: **[aicompanion_test.py](../aicompanion_test.py)**

Interfaccia dedicata all’interrogazione automatizzata: il sistema genera domande, l’utente risponde e l’AI valuta il risultato.

Funzionalità:
- Domanda corrente generata dal sistema
- Campo per l’inserimento della risposta dello studente
- Valutazione automatica (CORRETTA / SBAGLIATA)
- Spiegazione dettagliata fornita dal modello
- Gestione sessione + riepilogo finale con punteggio

![ Screenshot Chat interrogazione](../screen/test.png)