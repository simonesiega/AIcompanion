
import os

from langchain_ollama import OllamaEmbeddings

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import InMemoryVectorStore

from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import (
    EmbeddingConfig,
)


def choose_splitter(text_length: int, custom_size: int | None = None, custom_overlap: int | None = None) -> RecursiveCharacterTextSplitter:
    """
    Sceglie dinamicamente i parametri di suddivisione (chunking) del testo
    in base alla lunghezza complessiva o a parametri personalizzati.

    Parametri:
    -----------
        text_length (int): Numero totale di caratteri del testo.
        custom_size (int | None): Dimensione personalizzata di ciascun chunk.
        custom_overlap (int | None): Numero di caratteri sovrapposti tra chunk adiacenti.

    Restituisce:
    -------------
        RecursiveCharacterTextSplitter: Oggetto configurato per la suddivisione del testo.
    """

    # Se l’utente ha fornito parametri personalizzati
    if custom_size and custom_overlap:
        size, overlap = custom_size, custom_overlap

    # Testo breve → chunk piccoli con maggiore sovrapposizione 
    elif text_length < 3000:
        size, overlap = 500, 100

    # Testo medio → dimensioni intermedie e ridondanza bilanciata
    elif text_length < 10000:
        size, overlap = 800, 150

    # Testo lungo → chunk grandi con meno sovrapposizione 
    else:
        size, overlap = 1200, 250

    print(f"[choose_splitter] Impostato chunk_size={size}, overlap={overlap}")

    # Restituisce lo splitter configurato 
    return RecursiveCharacterTextSplitter(
        chunk_size=size, # Dimensione massima del singolo chunk
        chunk_overlap=overlap,  # Numero di caratteri condivisi tra due chunk consecutivi
        length_function=len, # Metodo di misura della lunghezza (numero di caratteri)
        is_separator_regex=False # Non interpreta i separatori come espressioni regolari
    )


def load_pdfs(data_dir: str = "./vs/data") -> list:
    """
    Carica tutti i file PDF da una cartella e li suddivide in chunk testuali.

    Parametri:
    -----------
        data_dir (str): Percorso alla cartella contenente i file PDF da processare.

    Restituisce:
    -------------
        list: Lista di Document (chunk) utilizzabili per creare il Vector Store.
    """

    chunks = []  # lista che conterrà tutti i blocchi di testo

    # Controllo cartella 
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"La cartella specificata non esiste: {data_dir}")

    for file in os.listdir(data_dir):
        if not file.endswith(".pdf"):
            continue  # ignora file non PDF

        file_path = os.path.join(data_dir, file)
        print(f"[load_pdfs] Caricamento di: {file_path}")

        try:
            # Carica il PDF e ottiene le pagine come documenti
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            # Combina tutto il testo per calcolare la lunghezza complessiva
            total_text = " ".join(doc.page_content for doc in docs)

            # Sceglie automaticamente lo splitter ottimale
            splitter = choose_splitter(len(total_text))

            # Divide i documenti in chunk testuali
            split_docs = splitter.split_documents(docs)

            # Aggiunge i chunk alla lista principale
            chunks.extend(split_docs)

        except Exception as e:
            print(f"Errore nel caricamento di {file}: {e}")

    print(f"Totale chunk creati: {len(chunks)}")
    return chunks


def create_vectorstore(chunks: list, db_path: str = "./vs/data.db", embedding_model: str = EmbeddingConfig.NAME) -> InMemoryVectorStore:
    """
    Crea e salva un VectorStore locale a partire da una lista di chunk testuali.

    Parametri:
    -----------
        chunks (list): Lista di oggetti Document contenenti testo da indicizzare.
        db_path (str): Percorso del file .db dove salvare il VectorStore generato.
        embedding_model (str): Nome del modello Ollama da usare per calcolare gli embedding.

    Restituisce:
    -------------
        InMemoryVectorStore: Il VectorStore generato e pronto all'uso.
    """

    if not chunks:
        raise ValueError("La lista dei chunk è vuota: impossibile creare il VectorStore.")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # crea la cartella se non esiste

    # Inizializza il modello di embedding 
    embeddings = OllamaEmbeddings(model=embedding_model)

    # Crea il VectorStore a partire dai documenti 
    vs = InMemoryVectorStore.from_documents(chunks, embeddings)

    # Salva su disco il database vettoriale 
    vs.dump(db_path)

    print(f"VectorStore creato con {len(chunks)} chunk e salvato in: {db_path}")

    return vs


def load_DB(data_dir="./vs"):
    """
    Carica tutti i database vettoriali (.db) presenti nella cartella /vs
    e li unisce in un unico InMemoryVectorStore.

    Parametri:
        data_dir (str): Directory contenente i file .db

    Restituisce:
        InMemoryVectorStore: Unione di tutti i VectorStore caricati
    """
    embeddings = OllamaEmbeddings(model=EmbeddingConfig.NAME)
    stores = []

    for file in os.listdir(data_dir):
        if file.endswith(".db"):
            file_path = os.path.join(data_dir, file)
            vs = InMemoryVectorStore.load(file_path, embeddings)
            stores.append(vs)

    # Nessun .db trovato
    if not stores:
        raise FileNotFoundError(f"Nessun file .db trovato in {data_dir}")

    # Unisce tutti i VectorStore caricati in uno unico
    combined = stores[0]
    for s in stores[1:]:
        combined.merge_from(s)

    print(f"Caricati correttamente {len(stores)} database vettoriali da {data_dir}")
    return combined


def get_relevant_chunks(question: str, vs: InMemoryVectorStore, embedding_model: str = EmbeddingConfig.NAME,top_k: int = 5) -> list[str]:
    """
    Restituisce i chunk più rilevanti rispetto a una domanda fornita dall'utente.

    Parametri:
    -----------
        question (str): Domanda o query dell’utente.
        vs (InMemoryVectorStore): Database vettoriale già caricato in memoria.
        embedding_model (str): Nome del modello Ollama da usare per calcolare l’embedding della query.
        top_k (int): Numero di risultati più rilevanti da restituire (default = 5).

    Restituisce:
    -------------
        list[str]: Lista dei contenuti testuali (page_content) dei chunk più pertinenti.
    """

    #  Validazione degli input 
    if not question.strip():
        raise ValueError("La domanda fornita è vuota.")
    if vs is None:
        raise ValueError("Il VectorStore fornito è None. Carica prima un database vettoriale valido.")

    # Calcola l'embedding della domanda 
    embeddings = OllamaEmbeddings(model=embedding_model)
    question_embedding = embeddings.embed_query(question)

    # Esegue la ricerca semantica basata sulla similarità vettoriale 
    results = vs.similarity_search_by_vector(question_embedding, k=top_k)

    # Estrae il contenuto testuale dei chunk trovati 
    relevant_chunks = [r.page_content for r in results]

    # Log di riepilogo utile per il debug
    print(f"[get_relevant_chunks] Trovati {len(relevant_chunks)} chunk rilevanti per la query: \"{question}\"")

    return relevant_chunks



