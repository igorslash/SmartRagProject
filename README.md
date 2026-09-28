# Smart RAG API with Observability

Локальный RAG (Retrieval-Augmented Generation) пайплайн с автоматической классификацией документов, семантической фильтрацией и полным трейсингом запросов.

## 🏗 Архитектура и Стек

- **LLM:** Ollama (llama3.2:3b) - полностью локальный инференс без API-ключей.
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`).
- **Vector DB:** ChromaDB (персистентное хранение на диске).
- **Framework:** LlamaIndex Core.
- **API:** FastAPI + Pydantic v2 + Uvicorn (с современным `lifespan`).
- **Observability:** Arize Phoenix (пошаговый трейсинг Retrieval и Generation).

## ✨ Ключевые особенности

- **Smart Metadata Extraction:** Использование `TitleExtractor` для автоматического чтения документов LLM и присвоения им семантических заголовков при загрузке.
- **Semantic Filtering:** Эндпоинт `/ask` поддерживает фильтрацию поиска по извлеченным метаданным (`document_title`), что снижает шум и предотвращает галлюцинации.
- **Optimized Chunking:** Настроенный `SentenceSplitter` (chunk_size=256, overlap=50) для борьбы с эффектом "Lost in the Middle".
- **Confidence Scoring:** API возвращает уровень уверенности (`high`/`low`) на основе `score` retrieved nodes.
- **Zero External Dependencies:** Весь пайплайн работает локально, данные не покидают контур пользователя.

## 🚀 Как запустить

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
