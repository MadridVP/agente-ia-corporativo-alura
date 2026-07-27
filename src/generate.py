"""
Paso 5 del pipeline RAG: generación de respuesta y control de alucinación.

Reglas clave:
1. Si retrieval.py no encontró contexto suficientemente relevante
   (por debajo del umbral), NUNCA se llama al LLM: se responde directo
   que no se tiene esa información.
2. Si hay contexto, el prompt obliga al LLM a responder SOLO con base
   en él, citando la fuente, y a admitir cuando no sepa la respuesta.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from retrieval import buscar_contexto

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")

MENSAJE_SIN_INFO = (
    "No encontré esta información en los documentos disponibles. "
    "Este agente solo responde con base en los documentos internos de BimBam Buy "
    "(reembolsos, envíos, FAQ, programa de afiliados y garantía)."
)

PROMPT_SISTEMA = """Eres el asistente virtual interno de BimBam Buy, una tienda en línea.
Respondes preguntas de los colaboradores basándote ÚNICAMENTE en el contexto
proporcionado a continuación, extraído de los documentos oficiales de la empresa.

Reglas obligatorias:
- No uses conocimiento externo ni información que no esté en el contexto.
- Si el contexto no contiene la respuesta a la pregunta, responde exactamente:
  "No encontré esta información en los documentos disponibles."
- Nunca inventes datos, cifras, plazos ni políticas.
- Al final de tu respuesta, indica siempre de qué documento(s) proviene la información,
  en el formato: (Fuente: nombre_archivo, página X)
- Responde en español, de forma clara y directa.
"""


def _armar_contexto(fragmentos: list[dict]) -> str:
    bloques = []
    for f in fragmentos:
        meta = f["metadata"]
        bloques.append(
            f"[Documento: {meta['archivo']} | Página: {meta['pagina']} | "
            f"Categoría: {meta['categoria']}]\n{f['texto']}"
        )
    return "\n\n---\n\n".join(bloques)


def responder(pregunta: str, categoria: str | None = None) -> dict:
    resultado = buscar_contexto(pregunta, categoria=categoria)

    if not resultado["hay_contexto"]:
        return {"respuesta": MENSAJE_SIN_INFO, "fuentes": []}

    fragmentos = resultado["fragmentos"]
    contexto = _armar_contexto(fragmentos)

    modelo = genai.GenerativeModel(
        model_name=LLM_MODEL,
        system_instruction=PROMPT_SISTEMA,
    )

    respuesta_llm = modelo.generate_content(
        f"Contexto:\n{contexto}\n\nPregunta del colaborador: {pregunta}",
        generation_config={"temperature": 0.1},
    )

    texto_respuesta = respuesta_llm.text

    fuentes = [
        {"archivo": f["metadata"]["archivo"], "pagina": f["metadata"]["pagina"]}
        for f in fragmentos
    ]

    return {"respuesta": texto_respuesta, "fuentes": fuentes}