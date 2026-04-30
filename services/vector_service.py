import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import GOOGLE_API_KEY

# Path untuk database vector
CHROMA_PATH = "db/chroma_db"

def get_vector_db():
    """Menginisialisasi atau memuat database vector."""
    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY tidak ditemukan di environment variables.")
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    # Initialize Chroma client
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    return client, embeddings

def ingest_pdf(pdf_path: str):
    """Membaca PDF dan memasukkannya ke dalam Vector DB."""
    if not os.path.exists(pdf_path):
        print(f"File tidak ditemukan: {pdf_path}")
        return

    # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Get Vector DB & Embeddings
    client, embeddings = get_vector_db()
    
    # Get or create collection
    collection = client.get_or_create_collection(name="pedoman_akademik")
    
    # 4. Add to Collection
    # Kita perlu mengkonversi format LangChain ke format ChromaDB
    ids = [f"id_{i}" for i in range(len(chunks))]
    texts = [chunk.page_content for chunk in chunks]
    
    # Generate embeddings
    embedded_texts = embeddings.embed_documents(texts)
    
    collection.add(
        ids=ids,
        embeddings=embedded_texts,
        documents=texts
    )
    
    print(f"[OK] Berhasil memasukkan {len(chunks)} bagian teks ke Vector DB.")

def search_vector_db(query: str, n_results: int = 3):
    """Mencari informasi yang relevan di Vector DB."""
    client, embeddings = get_vector_db()
    
    try:
        collection = client.get_collection(name="pedoman_akademik")
    except:
        return []
        
    # Generate embedding for query
    query_embedding = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    return results['documents'][0] if results['documents'] else []
