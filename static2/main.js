// Contenitore principale della chat 
const chat = document.getElementById('chat');

// Input di testo dove l'utente scrive la propria risposta
const rispostaInput = document.getElementById('risposta');

// Pulsante per inviare la risposta
const sendBtn = document.getElementById('sendBtn');

// Indice corrente della domanda in corso
let currentIndex = 0;

// Numero totale di domande disponibili
let totale = 0;

/**
 * setBusy: abilita o disabilita i controlli della UI
 * durante l'elaborazione di una richiesta per evitare input multipli.
 *
 * @param {boolean} state - true = blocca input, false = sblocca input
 */
function setBusy(state) {
    // Disabilita/abilita il pulsante di invio
    sendBtn.disabled = state;

    // Disabilita/abilita il campo di input testo
    rispostaInput.disabled = state;
}

/**
 * appendMessage: aggiunge un messaggio alla chat.
 * 
 * @param {string} text - Contenuto del messaggio da visualizzare
 * @param {string} who - 'user' per messaggi dell'utente, 'ai' per messaggi della AI (default: 'ai')
 * @param {boolean} html - Se true, il contenuto viene interpretato come HTML; altrimenti come testo semplice
 */
function appendMessage(text, who='ai', html=false) {
    // Crea un nuovo elemento <div> per il messaggio
    const div = document.createElement('div');

    // Imposta la classe CSS per il messaggio (user o ai) per lo styling
    div.className = 'msg ' + (who === 'user' ? 'user' : 'ai');

    // Inserisce il contenuto come HTML o come testo semplice
    if (html) div.innerHTML = text;
    else div.textContent = text;

    // Aggiunge il messaggio al contenitore della chat
    chat.appendChild(div);

    // Scorre automaticamente la chat verso il basso per mostrare il nuovo messaggio
    chat.scrollTop = chat.scrollHeight;
}

/**
 * startTest: Avvia l'interrogazione AI e mostra la prima domanda.
 * 
 * Questa funzione:
 * 1. Disabilita temporaneamente i controlli della UI 
 * 2. Fa una richiesta GET all'endpoint "/test_interrogazione/start" del backend Flask.
 * 3. Legge la risposta JSON 
 * 4. Aggiorna la chat con argomento, contesto e domanda iniziale.
 * 5. Aggiorna le variabili `currentIndex` e `totale` per la gestione della sessione.
 * 6. Riabilita i controlli UI una volta completata la richiesta.
*/
async function startTest() {
// Blocca input e pulsante invio durante l'elaborazione
    setBusy(true);

    try {
        // Richiesta al backend per avviare l'interrogazione
        const res = await fetch("/test_interrogazione/start");
        const data = await res.json();

        // Se c'è un errore restituito dal server, mostra il messaggio e termina
        if (data.error) {
            appendMessage(data.error);
            return;
        }

        // Mostra in chat l'argomento dell'interrogazione
        appendMessage("Argomento: " + data.topic);

        // Mostra in chat il contesto relativo alle domande
        appendMessage("Contesto: " + data.contesto);

        // Mostra in chat la prima domanda
        appendMessage("Domanda: " + data.domanda);

        // Aggiorna variabili di sessione
        currentIndex = data.index;
        totale = data.totale;

    } 
    catch (err) {
        // Gestione errori di rete o altri problemi di fetch
        appendMessage("Errore: " + err.message);
    } 
    finally {
        // Riabilita input e pulsante invio
        setBusy(false);
    }
}

/**
 * sendAnswer: Invia la risposta dell'utente al backend e gestisce la
 *             prossima domanda o il riepilogo finale dell'interrogazione.
 */
async function sendAnswer() {
    // Legge e pulisce il testo inserito dall'utente
    const risposta = rispostaInput.value.trim();
    if (!risposta) return; 

    // Mostra la risposta nella chat come messaggio dell'utente
    appendMessage(risposta, 'user');

    // Pulisce il campo input
    rispostaInput.value = '';

    // Blocca i controlli durante l'elaborazione
    setBusy(true);

    try {
        // Invio della risposta al backend tramite POST
        const res = await fetch("/test_interrogazione/answer", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({risposta})
        });

        // Legge la risposta JSON dal server
        const data = await res.json();

        // Se c'è una valutazione, mostra valutazione e spiegazione
        if (data.valutazione) {
            appendMessage("Valutazione: " + data.valutazione.valutazione);
            if (data.valutazione.spiegazione)
                appendMessage("Spiegazione: " + data.valutazione.spiegazione);
        }

        // Controlla se l'interrogazione è terminata
        if (data.finished) {
            appendMessage("Interrogazione terminata!");
            appendMessage(`Corrette: ${data.correte || 0} su ${data.totale}`);
        } 
        else {
            // Altrimenti mostra la prossima domanda
            appendMessage("Domanda successiva: " + data.next_domanda);
            currentIndex = data.index;
        }
    } 
    catch (err) {
        // Gestione errori di rete o backend
        appendMessage("Errore invio risposta: " + err.message);
    } 
    finally {
        // Riabilita input e pulsante invio
        setBusy(false);
    }
}

/* 
 * Invio tramite tasto Enter:
 * Permette di inviare la risposta premendo Enter all'interno del campo input.
 * - Previene il comportamento di default (a capo o submit del form)
 * - Chiama la funzione sendAnswer
 */
rispostaInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendAnswer();
    }
});

/* 
 * Avvio automatico dell'interrogazione:
 * Chiama la funzione startTest non appena viene caricato lo script,
 * in modo da mostrare subito la prima domanda e il contesto.
 */
startTest();
