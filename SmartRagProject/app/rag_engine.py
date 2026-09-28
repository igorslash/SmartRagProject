from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.extractors import TitleExtractor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.filters import MetadataFilters, ExactMatchFilter
import chromadb

from app.config import (
    DOCS_PATH, CHROMA_PATH, COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP
)
from app.logger import get_logger
from llama_index.core import Settings

logger = get_logger("rag_engine")

_index = None


def load_index():
    """Загружает или создаёт индекс при старте сервера."""
    global _index
    
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    if chroma_collection.count() > 0:
        _index = VectorStoreIndex.from_vector_store(vector_store)
        logger.info("index_loaded_from_db", documents_count=chroma_collection.count())
        return
    
    documents = SimpleDirectoryReader(DOCS_PATH).load_data()
    logger.info("documents_loaded", count=len(documents))
    
    title_extractor = TitleExtractor(llm=Settings.llm, nodes=5)
    logger.info("extracting_titles")
    transformed_docs = title_extractor(documents)
    
    for doc in transformed_docs:
        title = doc.metadata.get("document_title", "Без названия")
        logger.debug("title_extracted", file=doc.metadata.get("file_name", "?"), title=title)
    
    node_parser = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    _index = VectorStoreIndex.from_documents(
        transformed_docs,
        storage_context=storage_context,
        transformations=[node_parser]
    )
    logger.info("index_created", chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def get_index():
    """Возвращает текущий индекс."""
    return _index


def query_index(question: str, title_filter: str = ""):
    """Выполняет запрос к индексу."""
    if _index is None:
        logger.error("index_not_loaded")
        raise RuntimeError("Индекс не загружен")
    
    filters = None
    if title_filter:
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(
                    key="document_title",
                    value=title_filter
                )
            ]
        )
    
    query_engine = _index.as_query_engine(
        filters=filters,
        similarity_top_k=3
    )
    
    logger.info("query_executing", question=question[:50], filter=title_filter)
    response = query_engine.query(question)
    logger.info("query_completed", sources_count=len(response.source_nodes or []))
    
    return response