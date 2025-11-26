// Contenitore principale della chat dove verranno inseriti i messaggi
const chat = document.getElementById('chat');
// Input di testo dove l'utente scrive i messaggi
const msgInput = document.getElementById('message');
// Pulsante per inviare messaggi di testo
const sendBtn = document.getElementById('sendBtn');
// Pulsante per avviare/fermare la registrazione audio
const recBtn = document.getElementById('recBtn');
// Pulsante per riprodurre l'audio registrato in anteprima
const playBtn = document.getElementById('playBtn');
// Pulsante per inviare l'audio registrato al backend
const sendAudioBtn = document.getElementById('sendAudioBtn');
// Pulsante per scaricare l'audio registrato
const downloadBtn = document.getElementById('downloadBtn');
// Elemento <audio> per l'anteprima dell'audio registrato
const previewAudio = document.getElementById('previewAudio');
// Checkbox per indicare se si vuole ricevere la risposta del bot anche in audio (TTS)
const ttsFlag = document.getElementById('ttsFlag');

// Endpoint per inviare messaggi di testo
const TEXT_ENDPOINT = '/test';
// Endpoint per inviare messaggi audio
const AUDIO_ENDPOINT = '/audio';

// Blob contenente l'audio registrato dall'utente
let recordedBlob = null;
// Oggetto MediaRecorder utilizzato per registrare l'audio dal microfono
let recorder = null;
// Array che raccoglie i chunk dell'audio durante la registrazione
let chunks = [];
// Flag booleano per indicare se il sistema sta elaborando una richiesta
let isProcessing = false;

// setBusy: abilita o disabilita tutti i controlli della UI
// durante l'elaborazione di una richiesta per evitare input multipli
// state = true → blocca pulsanti e input
// state = false → sblocca pulsanti e input
function setBusy(state) {
	isProcessing = state;              // Aggiorna flag globale di stato
	sendBtn.disabled = state;          // Blocca/abilita invio testo
	recBtn.disabled = state;           // Blocca/abilita registrazione
	sendAudioBtn.disabled = state;     // Blocca/abilita invio audio
	msgInput.disabled = state;         // Blocca/abilita input testo
}

// appendMessage: aggiunge un messaggio alla chat
// text = contenuto del messaggio
// who = 'user' o 'ai' per differenziare lo stile
// html = true se il testo contiene HTML già formattato
function appendMessage(text, who = 'ai', html = false) {
	const div = document.createElement('div');
	div.className = 'msg ' + (who === 'user' ? 'user' : 'ai'); // Imposta classe per styling

	if (html) div.innerHTML = text;   // Inserisce il contenuto come HTML
	else div.textContent = text;      // Inserisce il contenuto come testo semplice

	chat.appendChild(div);
	chat.scrollTop = chat.scrollHeight; // Scroll automatico verso il basso
}

// appendBotAudio: aggiunge un messaggio audio del bot nella chat
// base64Audio = stringa base64 dell'audio generato dal bot
// text = trascrizione testuale opzionale da mostrare sopra l'audio
function appendBotAudio(base64Audio, text = '') {
	const container = document.createElement('div');
	container.className = 'msg ai';

	// Se presente una trascrizione, la aggiunge sopra l'audio
	if (text) {
		const p = document.createElement('p');
		p.textContent = text;
		container.appendChild(p);
	}

	// Decodifica base64 → stringa binaria
	const bytes = atob(base64Audio);
	// Crea array di byte
	const arr = new Uint8Array(bytes.length);
	for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);

	// Crea un Blob audio e imposta la sorgente dell'elemento <audio>
	const audio = document.createElement('audio');
	audio.controls = true;
	audio.src = URL.createObjectURL(new Blob([arr], { type: 'audio/wav' }));
	container.appendChild(audio);

	// Aggiunge il messaggio alla chat e scroll automatico
	chat.appendChild(container);
	chat.scrollTop = chat.scrollHeight;

	// Riproduzione automatica appena arriva l'audio
	audio.play().catch(err => {
		console.log('Autoplay fallito:', err);
	});
}

// playTTS: riproduce un audio generato dal TTS (Text-to-Speech)
// base64Str = stringa base64 contenente l'audio WAV
function playTTS(base64Str) {
	// Decodifica la stringa base64 in una stringa binaria
	const bytes = atob(base64Str);
	// Converte la stringa binaria in un array di byte (Uint8Array)
	const arr = new Uint8Array(bytes.length);
	for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);

	// Crea un Blob con MIME type audio/wav
	const blob = new Blob([arr], { type: 'audio/wav' });

	// Crea un oggetto Audio e assegna come sorgente il Blob appena creato
	const audio = new Audio(URL.createObjectURL(blob));

	// Riproduzione automatica appena arriva l'audio
	audio.play().catch(err => {
		console.log('Autoplay TTS fallito:', err);
	});
}

// sendTextMessage: invia il testo scritto dall'utente al backend
// Se il flag TTS è attivo, chiede anche la risposta vocale
async function sendTextMessage() {
	const message = msgInput.value.trim();
	// Se non c'è messaggio o è già in corso un'elaborazione, esce
	if (!message || isProcessing) return;

	// Mostra il messaggio dell'utente nella chat
	appendMessage(message, 'user');
	msgInput.value = '';

	// Disabilita i controlli mentre il messaggio viene elaborato
	setBusy(true);

	try {
		// Se il flag TTS è selezionato, aggiunge il parametro alla query
		const ttsQuery = ttsFlag.checked ? '?tts=1' : '';

		// Invia il messaggio al backend (endpoint /test) via POST
		const res = await fetch(TEXT_ENDPOINT + ttsQuery, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ message })
		});

		// Legge la risposta JSON dal server
		const data = await res.json();

		// Se la risposta contiene audio base64, aggiungi messaggio audio del bot
		if (data.base64) appendBotAudio(data.base64, data.response || '');
		// Altrimenti mostra la risposta testuale
		else appendMessage(data.response || JSON.stringify(data), 'ai', true);

	} catch (err) {
		// In caso di errore di rete o backend, mostra l'errore nella chat
		appendMessage('Errore: ' + err.message);
	} finally {
		// Riabilita i controlli dopo l'elaborazione
		setBusy(false);
	}
}

// sendAudioMessage: invia l'audio registrato dall'utente al backend
// Gestisce anche la risposta del bot come testo o audio (TTS)
async function sendAudioMessage() {
	// Se non c'è un audio registrato o è già in corso un'elaborazione, esce
	if (!recordedBlob || isProcessing) return;

	// Disabilita i controlli mentre l'audio viene elaborato
	setBusy(true);

	try {
		// Se il flag TTS è selezionato, aggiunge il parametro alla query
		const ttsQuery = ttsFlag.checked ? '?tts=1' : '';

		// Invia l'audio al backend (endpoint /audio) via POST
		const res = await fetch(AUDIO_ENDPOINT + ttsQuery, {
			method: 'POST',
			body: recordedBlob
		});

		// Legge la risposta JSON dal server
		const data = await res.json();

		// Mostra l'audio inviato dall'utente e la trascrizione
		appendUserAudio(recordedBlob, data.user || 'Trascrizione non disponibile');

		// Mostra la risposta del bot: audio + trascrizione se disponibile
		if (data.base64) appendBotAudio(data.base64, data.response || '');
		else appendMessage(data.response || JSON.stringify(data), 'ai', true);

	} catch (err) {
		// In caso di errore di rete o backend, mostra l'errore nella chat
		appendMessage('Errore upload: ' + err.message);
	} finally {
		// Pulizia dell'anteprima audio
		previewAudio.src = '';
		previewAudio.hidden = true;

		// Reset variabili e disabilita pulsanti
		recordedBlob = null;
		playBtn.disabled = true;
		sendAudioBtn.disabled = true;
		downloadBtn.disabled = true;

		// Ripristina testo del pulsante di registrazione
		recBtn.textContent = '🎙️';

		// Riabilita i controlli dopo l'elaborazione
		setBusy(false);
	}
}

// Quando l’utente clicca sul pulsante di registrazione
recBtn.addEventListener('click', async () => {
	// Se il registratore è già attivo, interrompe la registrazione
	if (recorder && recorder.state === 'recording') {
		recorder.stop();
		return;
	}

	try {
		// Richiede il permesso di accedere al microfono
		const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

		// Inizializza il buffer dei chunk audio
		chunks = [];

		// Crea un nuovo oggetto MediaRecorder per registrare l’audio del microfono
		recorder = new MediaRecorder(stream);

		// Ogni volta che riceve un blocco di dati audio, lo aggiunge all’array chunks
		recorder.ondataavailable = e => chunks.push(e.data);

		// Quando la registrazione termina (onstop)
		recorder.onstop = () => {
			// Combina tutti i chunk in un unico Blob audio in formato WebM
			recordedBlob = new Blob(chunks, { type: 'audio/webm' });

			// Mostra l’anteprima audio nell’interfaccia
			previewAudio.src = URL.createObjectURL(recordedBlob);
			previewAudio.hidden = false;

			// Abilita i pulsanti per riprodurre, inviare o scaricare l’audio
			playBtn.disabled = false;
			sendAudioBtn.disabled = false;
			downloadBtn.disabled = false;
		};

		// Avvia la registrazione
		recorder.start();

		// Cambia il testo del pulsante per indicare che la registrazione è in corso
		recBtn.textContent = '⏹️';
	} catch (err) {
		// Se il microfono non è accessibile o l’utente nega il permesso
		alert('Errore microfono: ' + err.message);
	}
});

// Riproduce l’audio registrato in anteprima
playBtn.addEventListener('click', () => previewAudio.play());

// Invia l’audio registrato al server per la trascrizione e la risposta del bot
sendAudioBtn.addEventListener('click', sendAudioMessage);

// Consente di scaricare l’audio registrato in locale come file .webm
downloadBtn.addEventListener('click', () => {
	// Se non c’è alcuna registrazione, interrompe l’azione
	if (!recordedBlob) return;

	// Crea dinamicamente un link “invisibile” per forzare il download
	const a = document.createElement('a');
	a.href = URL.createObjectURL(recordedBlob); // converte il Blob in un URL temporaneo
	a.download = 'registrazione.webm';          // nome del file scaricato
	a.click();                                  // simula il click sul link per scaricare
});

// appendUserAudio: Mostra nella chat l’audio inviato dall’utente e, sotto di esso,
// la trascrizione generata da Whisper (se disponibile).
function appendUserAudio(blob, transcription) {
	const container = document.createElement('div');
	container.className = 'msg user';

	// Crea il player audio per riascoltare la registrazione
	const audio = document.createElement('audio');
	audio.controls = true;
	audio.src = URL.createObjectURL(blob);
	container.appendChild(audio);

	// Aggiunge la trascrizione (se presente)
	if (transcription) {
		const p = document.createElement('p');
		p.textContent = transcription;
		container.appendChild(p);
	}

	// Inserisce il messaggio completo nella chat
	chat.appendChild(container);
	// Fa scorrere automaticamente la chat verso il basso
	chat.scrollTop = chat.scrollHeight;
}

// Click sul pulsante “Invia”
sendBtn.addEventListener('click', sendTextMessage);

// Pressione del tasto Invio nel campo di testo
msgInput.addEventListener('keydown', e => {
	// Previene l’invio multiplo o l’invio accidentale con Shift+Enter
	if (e.key === 'Enter') {
		e.preventDefault();
		sendTextMessage();
	}
});