import sys
import os
from pathlib import Path

# Add parent directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.vector_service import (
    ingest_pdf,
    ingest_text_file,
    ingest_json_file,
    ingest_json_data,
    list_collections,
    delete_collection,
    search_multiple_collections
)
import json

def ingest_dataset(dataset_path: str, collection_name: str = None):
    """
    Mengingest dataset berdasarkan tipe file.
    Mendukung: PDF, TXT, JSON
    """
    if not os.path.exists(dataset_path):
        print(f" File tidak ditemukan: {dataset_path}")
        return False

    # Tentukan collection name berdasarkan file jika tidak disediakan
    if collection_name is None:
        base_name = os.path.splitext(os.path.basename(dataset_path))[0]
        collection_name = f"dataset_{base_name.lower().replace(' ', '_')}"

    file_ext = os.path.splitext(dataset_path)[1].lower()

    try:
        if file_ext == '.pdf':
            ingest_pdf(dataset_path, collection_name)
        elif file_ext in ['.txt', '.md']:
            ingest_text_file(dataset_path, collection_name)
        elif file_ext == '.json':
            ingest_json_file(dataset_path, collection_name)
        else:
            print(f" Tipe file {file_ext} tidak didukung. Gunakan PDF, TXT, MD, atau JSON.")
            return False

        print(f" Dataset berhasil diingest ke collection: {collection_name}")
        return True

    except Exception as e:
        print(f" Error mengingest dataset: {str(e)}")
        return False

def ingest_directory(directory_path: str, collection_name: str = "bulk_knowledge"):
    """
    Mengingest semua file yang didukung dalam directory.
    """
    if not os.path.exists(directory_path):
        print(f" Directory tidak ditemukan: {directory_path}")
        return False

    supported_ext = ['.pdf', '.txt', '.md', '.json']
    ingested_count = 0

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in supported_ext:
            print(f" Mengingest: {filename}")
            if ingest_dataset(file_path, collection_name):
                ingested_count += 1

    print(f" Berhasil mengingest {ingested_count} file ke collection: {collection_name}")
    return ingested_count > 0

def add_knowledge_from_text(text: str, collection_name: str, source_name: str = "manual_input"):
    """
    Menambahkan knowledge dari text langsung.
    """
    try:
        from langchain_core.documents import Document
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # Create document
        document = Document(page_content=text)

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents([document])

        # Add to collection
        from services.vector_service import _add_chunks_to_collection
        _add_chunks_to_collection(chunks, collection_name, source_name)

        print(f" Knowledge berhasil ditambahkan ke collection: {collection_name}")
        return True

    except Exception as e:
        print(f" Error menambahkan knowledge: {str(e)}")
        return False

def add_knowledge_from_json(json_data: dict, collection_name: str, source_name: str = "json_input"):
    """
    Menambahkan knowledge dari data JSON.
    """
    try:
        ingest_json_data(json_data, collection_name, source_name)
        print(f" JSON knowledge berhasil ditambahkan ke collection: {collection_name}")
        return True
    except Exception as e:
        print(f" Error menambahkan JSON knowledge: {str(e)}")
        return False

def show_collections():
    """Menampilkan semua collections yang ada."""
    collections = list_collections()
    if collections:
        print(" Collections yang tersedia:")
        for col in collections:
            print(f"  - {col}")
    else:
        print(" Tidak ada collection yang tersedia.")

def clear_collection(collection_name: str):
    """Menghapus collection."""
    return delete_collection(collection_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ingest_dataset.py <file_path> [collection_name]")
        print("  python ingest_dataset.py --dir <directory_path> [collection_name]")
        print("  python ingest_dataset.py --text \"your text here\" <collection_name>")
        print("  python ingest_dataset.py --json <json_file> <collection_name>")
        print("  python ingest_dataset.py --list")
        print("  python ingest_dataset.py --clear <collection_name>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--list":
        show_collections()

    elif command == "--clear":
        if len(sys.argv) < 3:
            print(" Collection name diperlukan untuk --clear")
            sys.exit(1)
        clear_collection(sys.argv[2])

    elif command == "--dir":
        if len(sys.argv) < 3:
            print(" Directory path diperlukan")
            sys.exit(1)
        collection_name = sys.argv[3] if len(sys.argv) > 3 else None
        ingest_directory(sys.argv[2], collection_name)

    elif command == "--text":
        if len(sys.argv) < 4:
            print(" Text dan collection name diperlukan")
            sys.exit(1)
        add_knowledge_from_text(sys.argv[2], sys.argv[3])

    elif command == "--json":
        if len(sys.argv) < 4:
            print(" JSON file dan collection name diperlukan")
            sys.exit(1)
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            data = json.load(f)
        add_knowledge_from_json(data, sys.argv[3])

    else:
        # Ingest single file
        file_path = command
        collection_name = sys.argv[2] if len(sys.argv) > 2 else None
        ingest_dataset(file_path, collection_name)