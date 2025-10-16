// Flag che indica se l'AI sta elaborando una richiesta.
// Evita che l'utente invii più messaggi mentre la risposta è ancora in corso.
let isProcessing = false;

/**
 * Invia il messaggio dell’utente al backend Flask
 * e gestisce la risposta del modello AI.
 */
async function sendMessage() {
  // Se c'è già un messaggio in elaborazione, blocca l'invio
  if (isProcessing) return; 

  // Recupera input e pulsante
  const input = document.getElementById("user-input");
  const button = document.getElementById("send-btn");
  
  // Pulisce input utente e controlla che non sia vuoto
  const message = input.value.trim();
  if (!message) return;

  // Aggiunge subito il messaggio dell'utente nella chat
  addMessage("user", message);

  // Disabilita input e pulsante durante l'elaborazione
  input.value = "";
  input.disabled = true;
  button.disabled = true;
  isProcessing = true;

  // Mostra messaggio di attesa
  const thinking = addMessage("bot typing", "Sto pensando...");

  try {
    // Invia una richiesta POST al backend Flask (/test) con il messaggio dell'utente
    const response = await fetch("/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    // Se la risposta HTTP non è OK (200), genera un errore con il codice HTTP
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    // Converte la risposta JSON ricevuta dal server 
    const data = await response.json();

    // Rimuove il messaggio "Sto pensando..." dalla chat
    removeMessage(thinking);
    
    // Se la richiesta ha avuto successo, mostra la risposta dell'AI nella chat
    if (data.response) addMessage("bot", data.response);
    // Se il server ha restituito un errore, lo mostra nella chat
    else if (data.error) addMessage("bot", "-- Errore: " + data.error);
    
  } 
  
  catch (error) {
    // Se si verifica un errore di rete o altro durante fetch
    // rimuove il messaggio "Sto pensando..."
    removeMessage(thinking);

    // Mostra un messaggio di errore nella chat
    addMessage("bot", "- Errore di rete: " + error.message);
  } 
  
  finally {
    // Ripristina lo stato dell'input e del pulsante per permettere nuovi invii
    input.disabled = false;
    button.disabled = false;
    input.focus();

    // Non ci sono più messaggi in elaborazione
    isProcessing = false;
  }
}

/**
 * Aggiunge un messaggio alla chat.
 * @param {string} s - 'user', 'bot', o 'bot typing'
 * @param {string} text - contenuto del messaggio
 * @returns {HTMLElement} l’elemento messaggio creato
 */
function addMessage(s, text) {
  const chatBox = document.getElementById("chat-box");
  // Crea un nuovo div per il messaggio
  const msg = document.createElement("div");
  msg.classList.add("message");
  
  // Se il messaggio è di tipo "typing" (sta pensando), aggiunge la classe 'typing'
  if (s.includes("typing")) msg.classList.add("typing");
  // Altrimenti aggiunge la classe specifica 'user' o 'bot'
  else msg.classList.add(s);

  // Imposta il testo e aggiunge il messaggio appena creato alla chat
  msg.textContent = text;
  chatBox.appendChild(msg);

  // Scorre verso il basso per mostrare l'ultimo messaggio
  chatBox.scrollTop = chatBox.scrollHeight;

  return msg;
}

/**
 * Rimuove un messaggio (es. il “sta pensando...”)
 * @param {HTMLElement} element - l’elemento da rimuovere
 */
function removeMessage(element) {
  // Controlla che l'elemento esista e abbia un genitore nel DOM
  if (element && element.parentNode) element.parentNode.removeChild(element);
}

// Permette l’invio premendo "Enter"
document.getElementById("user-input").addEventListener("keydown", (e) => {
  // Se il tasto premuto è "Enter" e non c'è già un messaggio in elaborazione
  // Chiama la funzione sendMessage per inviare il messaggio 
  if (e.key === "Enter" && !isProcessing) sendMessage();
});
