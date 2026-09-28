from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Модели
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
Settings.llm = Ollama(model="llama3.2:3b", temperature=0.1)


DOCS_PATH = "./docs"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

# Параметры чанкинга 
CHUNK_SIZE = 256
CHUNK_OVERLAP = 50

# Порог уверенности 
CONFIDENCE_THRESHOLD = 0.7