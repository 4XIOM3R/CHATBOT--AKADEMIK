import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import GOOGLE_API_KEY
import json
from typing import List, Dict, Any

# Path untuk database vector
CHROMA_PATH = "db/chroma_db"

# Inisialisasi instance global untuk performa
_embeddings = None
_chroma_client = None

def get_vector_db():
    """Mengambil instance global database vector dan embeddings."""
    global _embeddings, _chroma_client
    
    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY tidak ditemukan di environment variables.")
        
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2", 
            google_api_key=GOOGLE_API_KEY
        )

    
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    return _chroma_client, _embeddings


def ingest_pdf(pdf_path: str, collection_name: str = "pedoman_akademik"):
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
    
    # 3. Add to Vector DB
    _add_chunks_to_collection(chunks, collection_name, f"pdf_{os.path.basename(pdf_path)}")
    
    print(f"[OK] Berhasil memasukkan {len(chunks)} bagian teks dari {pdf_path} ke collection '{collection_name}'.")


def ingest_text_file(text_path: str, collection_name: str = "general_knowledge"):
    """Membaca file teks dan memasukkannya ke dalam Vector DB."""
    if not os.path.exists(text_path):
        print(f"File tidak ditemukan: {text_path}")
        return

    # 1. Load Text
    loader = TextLoader(text_path, encoding='utf-8')
    documents = loader.load()

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Add to Vector DB
    _add_chunks_to_collection(chunks, collection_name, f"text_{os.path.basename(text_path)}")
    
    print(f"[OK] Berhasil memasukkan {len(chunks)} bagian teks dari {text_path} ke collection '{collection_name}'.")


def ingest_json_data(json_data: Dict[str, Any], collection_name: str, source_name: str = "json_data"):
    """Memasukkan data JSON ke dalam Vector DB."""
    # Ubah JSON menjadi potongan teks
    text_chunks = []
    
    if isinstance(json_data, dict):
        # Ubah dict menjadi teks terformat
        for key, value in json_data.items():
            if isinstance(value, (list, dict)):
                value = json.dumps(value, indent=2, ensure_ascii=False)
            text_chunks.append(f"{key}: {value}")
    elif isinstance(json_data, list):
        # Ubah list menjadi potongan teks
        for i, item in enumerate(json_data):
            if isinstance(item, dict):
                text_chunks.append(json.dumps(item, indent=2, ensure_ascii=False))
            else:
                text_chunks.append(str(item))
    else:
        text_chunks.append(str(json_data))
    
    # Buat dokumen LangChain
    from langchain_core.documents import Document
    documents = [Document(page_content=chunk) for chunk in text_chunks]
    
    # Pisahkan jika diperlukan
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    
    # Tambahkan ke Vector DB
    _add_chunks_to_collection(chunks, collection_name, source_name)
    
    print(f"[OK] Berhasil memasukkan {len(chunks)} bagian data JSON ke collection '{collection_name}'.")


def ingest_json_file(json_path: str, collection_name: str = "json_knowledge"):
    """Membaca file JSON dan memasukkannya ke dalam Vector DB."""
    if not os.path.exists(json_path):
        print(f"File tidak ditemukan: {json_path}")
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        source_name = f"json_{os.path.basename(json_path)}"
        ingest_json_data(json_data, collection_name, source_name)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {json_path}: {e}")
    except Exception as e:
        print(f"Error reading JSON file {json_path}: {e}")


def _add_chunks_to_collection(chunks, collection_name: str, source_prefix: str):
    """Helper function untuk menambahkan chunks ke collection."""
    # 3. Get Vector DB & Embeddings
    client, embeddings = get_vector_db()
    
    # Ambil atau buat koleksi
    collection = client.get_or_create_collection(name=collection_name)
    
    # 4. Add to Collection
    # Kita perlu mengkonversi format LangChain ke format ChromaDB
    ids = [f"{source_prefix}_{i}" for i in range(len(chunks))]
    texts = [chunk.page_content for chunk in chunks]
    
    # Buat embedding satu per satu untuk menghindari masalah library batching
    embedded_texts = [embeddings.embed_query(t) for t in texts]
    
    collection.add(
        ids=ids,
        embeddings=embedded_texts,
        documents=texts
    )


def search_vector_db(query: str, collection_name: str = "pedoman_akademik", n_results: int = 3):
    """Mencari informasi yang relevan di Vector DB beserta distance-nya."""
    client, embeddings = get_vector_db()
    
    try:
        collection = client.get_collection(name=collection_name)
    except:
        return []
        
    # Buat embedding untuk query
    query_embedding = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    if not results['documents'] or not results['documents'][0]:
        return []
        
    # Gabungkan dokumen dan distances untuk sorting nanti
    formatted_results = []
    for i in range(len(results['documents'][0])):
        formatted_results.append({
            "content": results['documents'][0][i],
            "distance": results['distances'][0][i] if 'distances' in results else 1.0
        })
        
    return formatted_results


def search_multiple_collections(query: str, collections: List[str] = None, n_results: int = 3):
    """Mencari informasi di multiple collections dan mengurutkan berdasarkan relevansi."""
    if collections is None:
        collections = ["pedoman_akademik", "general_knowledge", "json_knowledge"]
    
    all_results = []
    for collection_name in collections:
        results = search_vector_db(query, collection_name, n_results)
        if results:
            all_results.extend(results)
    
    # Sort berdasarkan distance terkecil (paling relevan)
    all_results.sort(key=lambda x: x['distance'])
    
    # Ambil konten saja
    final_docs = [res['content'] for res in all_results[:n_results]]
    
    return final_docs


def list_collections():
    """List semua collections yang ada."""
    client, _ = get_vector_db()
    try:
        collections = client.list_collections()
        return [col.name for col in collections]
    except:
        return []


def delete_collection(collection_name: str):
    """Menghapus collection."""
    client, _ = get_vector_db()
    try:
        client.delete_collection(name=collection_name)
        print(f"[OK] Collection '{collection_name}' berhasil dihapus.")
        return True
    except Exception as e:
        print(f"[ERROR] Gagal menghapus collection '{collection_name}': {e}")
        return False
