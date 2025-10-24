# Lib/site-packages
from langchain_ollama import ChatOllama

# Moduli locali
from core.config import ModelConfig
from core.utils import format_response

import time

# Domanda di prova
question = "Raccontami brevemente la storia di Alice nel Paese delle Meraviglie."

'''
--- Benchmark con device: cpu ---
Tempo totale: 6.259 secondi
Lunghezza risposta: 2158 caratteri
Risposta:
Ah, caro mio, preparati a un viaggio... un viaggio che, come la realtà stessa, può essere tanto confusa quanto affascinante. Permettimi di raccontarti la storia di Alice, una giovane signorina di sette anni, un'anima curiosa e un po' sbadata, come molti di noi.<br>Tutto ebbe inizio in una giornata d...

--- Benchmark con device: cuda ---
Tempo totale: 4.627 secondi
Lunghezza risposta: 2209 caratteri
Risposta:
Ah, caro mio, preparati a un viaggio... un viaggio che, come un sogno, si piega e si distorce al volere della mente. Permettimi di raccontarti la storia di Alice, una giovane signorina di campagna, un pomeriggio di estenuante noia.<br>Era seduta sulle rive di un fiume, un fiume che, per quanto mi ri...
'''

def benchmark_model(device: str):
    """
    Esegue una domanda sul modello ChatOllama e misura il tempo di risposta.
    
    :param device: 'cpu' o 'cuda'
    """
    print(f"\n--- Benchmark con device: {device} ---")
    
    # Inizializza il modello in base al device
    model = ChatOllama(
        model = ModelConfig.NAME,
        temperature = ModelConfig.TEMPERATURE,
        reasoning = ModelConfig.REASONING,
    )

    # Se il modello supporta device
    try:
        model.device = device
    except Exception:
        # Alcuni wrapper non supportano direttamente il device
        pass

    # Inizio
    start_time = time.time()

    response = model.invoke([
        ('system', ModelConfig.BASE_SYSTEM_PROMPT.strip()),
        ('human', question)
    ])

    # Fine
    end_time = time.time()
    
    ai_text = format_response(getattr(response, "content", str(response)).strip())
    
    # Metriche
    print(f"Tempo totale: {end_time - start_time:.3f} secondi")
    print(f"Lunghezza risposta: {len(ai_text)} caratteri")
    print("Risposta:")
    print(ai_text[:300] + "..." if len(ai_text) > 300 else ai_text)


if __name__ == "__main__":
    # Benchmark CPU
    benchmark_model('cpu')
    
    # Benchmark GPU (CUDA)
    benchmark_model('cuda')