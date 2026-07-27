# 🛍️ BimBam Buy — Agente de IA Corporativo (RAG)

Agente de inteligencia artificial corporativo desarrollado para el **Desafío Agentes de Alura Latam**. Responde preguntas de los colaboradores de **BimBam Buy** (empresa hipotética de e-commerce) basándose exclusivamente en sus documentos internos, citando siempre la fuente de la información.

---

## 📋 Descripción del proyecto

BimBam Buy es una tienda en línea que necesita centralizar el conocimiento disperso en sus documentos internos (políticas, FAQ, guías de envío, términos y condiciones) en un agente conversacional accesible para todos sus colaboradores, disponible 24/7.

El agente implementa el patrón **RAG (Retrieval-Augmented Generation)**: en lugar de que el modelo de lenguaje "invente" respuestas, primero busca los fragmentos más relevantes dentro de los documentos oficiales de la empresa y luego genera una respuesta basada únicamente en ese contexto, indicando siempre de qué documento proviene la información.

### Documentos utilizados

| Documento | Categoría |
|---|---|
| Política de privacidad | Legal |
| Política de reembolsos y devoluciones | Operacional |
| Preguntas frecuentes (FAQ) | Atención al cliente |
| Guía de envíos y entregas | Operacional |
| Términos y condiciones | Legal |

---

## 🏗️ Arquitectura
Colaborador
│
▼
Interfaz de chat (Streamlit)
│
▼
┌─────────────────────────────────────────┐
│ PIPELINE RAG │
│ │
│ 1. Extracción y limpieza de texto (PDF) │
│ 2. Chunking (fragmentos con overlap) │
│ 3. Embeddings (modelo de embeddings) │
│ 4. Indexación vectorial (ChromaDB) │
│ 5. Búsqueda semántica + metadatos │
│ 6. Generación de respuesta (LLM) │
│ 7. Citación de la fuente │
└─────────────────────────────────────────┘
│
▼
Respuesta + fuente citada (documento/sección)
│
▼
Desplegado en Oracle Cloud Infrastructure (OCI Compute)
---

## 🛠️ Tecnologías

- **Python 3.11**
- **LangChain** — orquestación del pipeline RAG
- **ChromaDB** — base de datos vectorial (embeddings)
- **sentence-transformers** — modelo de embeddings local
- **OpenAI API (gpt-4o-mini)** — generación de respuestas
- **Streamlit** — interfaz de chat web
- **PyPDF** — extracción de texto de PDFs
- **Oracle Cloud Infrastructure (OCI)** — servicio de despliegue: **OCI Compute** (instancia `instance-20260726-1518`, VM.Standard.E2.1.Micro, Oracle Linux 9, región US East - Ashburn)
---

## 📁 Estructura del repositorio

```
bimbam-buy-agente-rag/
├── README.md
├── requirements.txt
├── .env.example
├── docs/                     # Documentos originales de BimBam Buy
├── src/
│   ├── ingest.py             # Extracción, limpieza y chunking de documentos
│   ├── embeddings.py         # Generación de embeddings e indexación en ChromaDB
│   ├── retrieval.py          # Búsqueda semántica + filtrado por metadatos
│   ├── generate.py           # Generación de respuesta con el LLM + citación de fuente
│   └── app.py                # Interfaz de chat en Streamlit
└── chroma_db/                # Índice vectorial persistido (generado localmente)
```

---

## ⚙️ Instalación y ejecución local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/[TU-USUARIO]/bimbam-buy-agente-rag.git
   cd bimbam-buy-agente-rag
   ```

2. Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   ```bash
   copy .env.example .env
   ```
   Editar `.env` y agregar tu API key de OpenAI.

4. Procesar los documentos y generar el índice vectorial:
   ```bash
   python src/ingest.py
   python src/embeddings.py
   ```

5. Ejecutar la aplicación:
   ```bash
   streamlit run src/app.py
   ```

6. Abrir en el navegador: `http://localhost:8501`

---

## 💬 Ejemplos de preguntas y respuestas

**Pregunta:** ¿Cuántos días tengo para devolver un producto?
**Respuesta:** Según la Política de Reembolsos y Devoluciones, tienes 30 días calendario desde la recepción del producto para solicitar una devolución. *(Fuente: politica_reembolsos.pdf)*

**Pregunta:** ¿Cuál es la política de vacaciones de la empresa?
**Respuesta:** No encontré esta información en los documentos disponibles.

## ☁️ Despliegue en OCI

El agente fue desplegado en **Oracle Cloud Infrastructure**, utilizando el servicio **OCI Compute**:

- **Instancia:** `instance-20260726-1518`
- **Shape:** VM.Standard.E2.1.Micro (Always Free)
- **Imagen:** Oracle Linux 9
- **Región:** US East (Ashburn)
- **IP pública:** `129.158.228.36`

---

## 👤 Autor

**Patricia Madrid**
Challenge Tech con IA_Desafío Agentes_Alura Latam