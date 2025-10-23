"""
test_rag.py
-----------
Script per la generazione del Vector Store utilizzato nel sistema RAG.
Questo script:
1. Carica un file PDF
2. Lo suddivide in chunk testuali
3. Genera embeddings tramite un modello Ollama
4. Salva il VectorStore su disco per utilizzo in fase di runtime
"""   

# Lib/site-packages
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Moduli locali
from config import EmbeddingConfig

# py
import time
import os

def main():
    start_time = time.time()

    print("=== Generazione Vector Store Avviata ===")

    # Inizializzazione Embeddings
    print("Inizializzazione embeddings...")
    embedding_model = OllamaEmbeddings(
        model=EmbeddingConfig.NAME
    )

    # Caricamento Documento
    pdf_path = "./vs/data/carroll_alice_nel_etc_loescher.pdf"
    if not os.path.exists(pdf_path): raise FileNotFoundError(f"Il file PDF non è stato trovato: {pdf_path}")

    print(f"Caricamento documento da: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Documento caricato con successo. Numero pagine: {len(documents)}")

    # Suddivisione in Chunk
    print("Suddivisione del documento in chunk...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = EmbeddingConfig.CHUNK_SIZE,
        chunk_overlap = EmbeddingConfig.CHUNK_OVERLAP,
        length_function = EmbeddingConfig.LENGTH_FUNCTION,
        is_separator_regex = EmbeddingConfig.IS_SEPARATOR_REGEX
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Chunk generati: {len(chunks)}")

    # Creazione VectorStore
    print("Creazione Vector Store...")
    vector_store = InMemoryVectorStore.from_documents(chunks, embedding_model)
    print("Vector Store creato con successo.")

    # Salvataggio su Disco
    output_path = "./vs/alice.db"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Salvataggio Vector Store su: {output_path}")
    vector_store.dump(output_path)
    print("Salvataggio completato.")

    # Tempo totale
    total_time = time.time() - start_time
    print(f"\n=== Operazione completata in {total_time:.2f} secondi ===")

if __name__ == "__main__":
    main()