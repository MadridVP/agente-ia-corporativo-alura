"""
Paso 1 y 2 del pipeline RAG: colecta de documentos, extracción de texto,
limpieza y chunking (división en fragmentos con metadatos).
"""

import os
import re
import json
from pathlib import Path
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_FILE = Path(__file__).parent.parent / "chunks.json"

CATEGORIAS = {
    "politica_reembolsos.pdf": "Operacional",
    "programa_afiliados.pdf": "Marketing y Comercial",
    "guia_envios.pdf": "Operacional",
    "faq.pdf": "Atención al cliente",
    "manual_garantia.pdf": "Operacional",
},

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def limpiar_texto(texto: str) -> str:
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", texto)
    return texto.strip()


def extraer_pdf(ruta: Path) -> list[dict]:
    reader = PdfReader(str(ruta))
    paginas = []
    for i, page in enumerate(reader.pages, start=1):
        texto = limpiar_texto(page.extract_text() or "")
        if texto:
            paginas.append({"texto": texto, "pagina": i})
    return paginas


def chunkear_documento(nombre_archivo: str, paginas: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    categoria = CATEGORIAS.get(nombre_archivo, "Sin categoría")

    for pagina in paginas:
        fragmentos = splitter.split_text(pagina["texto"])
        for fragmento in fragmentos:
            chunks.append(
                {
                    "texto": fragmento,
                    "metadata": {
                        "archivo": nombre_archivo,
                        "categoria": categoria,
                        "pagina": pagina["pagina"],
                    },
                }
            )
    return chunks


def main():
    if not DOCS_DIR.exists():
        raise FileNotFoundError(
            f"No se encontró la carpeta {DOCS_DIR}. "
            "Coloca ahí los PDFs de BimBam Buy antes de correr este script."
        )

    todos_los_chunks = []
    archivos_pdf = sorted(DOCS_DIR.glob("*.pdf"))

    if not archivos_pdf:
        raise FileNotFoundError(f"No se encontraron PDFs en {DOCS_DIR}")

    for archivo in archivos_pdf:
        print(f"Procesando: {archivo.name}")
        paginas = extraer_pdf(archivo)
        chunks = chunkear_documento(archivo.name, paginas)
        print(f"  -> {len(chunks)} fragmentos generados")
        todos_los_chunks.extend(chunks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(todos_los_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(todos_los_chunks)} fragmentos guardados en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
