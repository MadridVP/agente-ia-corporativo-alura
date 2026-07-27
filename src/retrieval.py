"""
Paso 4 del pipeline RAG: capa de recuperación.
Convierte la pregunta en embedding, busca los fragmentos más cercanos
semánticamente en ChromaDB, y aplica un umbral de confianza: si nada
supera el umbral, no se le pasa contexto al LLM (evita alucinaciones).
"""

import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "bimbam_buy_docs"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # mismo modelo que embeddings.py

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
N_RESULTADOS = 5

_modelo = None
_coleccion = None


def _cargar_recursos():
    global _modelo, _coleccion
    if _modelo is None:
        _modelo = SentenceTransformer(EMBEDDING_MODEL)
    if _coleccion is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _coleccion = client.get_collection(COLLECTION_NAME)
    return _modelo, _coleccion


def buscar_contexto(pregunta: str, categoria: str | None = None) -> dict:
    modelo, coleccion = _cargar_recursos()
    vector_pregunta = modelo.encode([pregunta]).tolist()

    filtro = {"categoria": categoria} if categoria else None

    resultados = coleccion.query(
        query_embeddings=vector_pregunta,
        n_results=N_RESULTADOS,
        where=filtro,
    )

    fragmentos = []
    documentos = resultados["documents"][0]
    metadatas = resultados["metadatas"][0]
    distancias = resultados["distances"][0]

    for doc, meta, dist in zip(documentos, metadatas, distancias):
        similitud = max(0.0, 1 - dist)
        fragmentos.append({"texto": doc, "metadata": meta, "similitud": similitud})

    mejor_similitud = fragmentos[0]["similitud"] if fragmentos else 0.0
    hay_contexto = mejor_similitud >= SIMILARITY_THRESHOLD

    return {
        "hay_contexto": hay_contexto,
        "fragmentos": fragmentos if hay_contexto else [],
        "mejor_similitud": mejor_similitud,
    }