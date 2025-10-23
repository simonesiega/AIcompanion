from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import InMemoryVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter


import time
import os


# Embeddings
embedding = OllamaEmbeddings(
    model = "embeddinggemma:300m"
)


t_start = time.time()


# Load documento
loader = PyPDFLoader("./vs/data/carroll_alice_nel_etc_loescher.pdf")
docs = loader.load()
# print(len(docs)) - 136 = numero pagine pdf
print("Documento letto")


# Ulteriore suddivisione
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 500,
    length_function = len,
    is_separator_regex = False
)
chunks = text_splitter.split_documents(docs)
# print(len(chunks)) - 551
print("Chunk creti")


vs = InMemoryVectorStore.from_documents(chunks, embedding)
print("VectorStore creato")


vs.dump("./vs./alice.db")
print("VectoreStore salvato su disco")


print(f"Tempo: {(time.time() - t_start):.2f} secondi") # Tempo: 95 secondi

