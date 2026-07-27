"""
Paso 3 del pipeline RAG: indexación vectorial.
Genera embeddings de cada chunk (usando un modelo local, gratuito y
consistente) y los guarda en ChromaDB junto con sus metadatos.
"""

import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path(__file__).parent.parent / "chunks.json"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "bimbam_buy_docs"

# Modelo de embeddings multilingüe (funciona bien en español), local y gratuito.
# Importante: debe ser el MISMO modelo usado luego en retrieval.py.
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def cargar_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró {CHUNKS_FILE}. Corre primero: python src/ingest.py"
        )
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    chunks = cargar_chunks()
    print(f"Cargando modelo de embeddings ({EMBEDDING_MODEL})...")
    modelo = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Generando embeddings para {len(chunks)} fragmentos...")
    textos = [c["texto"] for c in chunks]
    vectores = modelo.encode(textos, show_progress_bar=True).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    coleccion = client.create_collection(COLLECTION_NAME)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [c["metadata"] for c in chunks]

    coleccion.add(
        ids=ids,
        embeddings=vectores,
        documents=textos,
        metadatas=metadatas,
    )

    print(f"\n{len(chunks)} fragmentos indexados en ChromaDB ({CHROMA_DIR})")


if __name__ == "__main__":
    main()