from fastapi import APIRouter
from app.models import QuestionRequest, AnswerResponse
from app.rag_engine import get_index, query_index
from app.config import CONFIDENCE_THRESHOLD

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "index_loaded": get_index() is not None
    }


@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if get_index() is None:
        return {"error": "Индекс не загружен."}
    
    response = query_index(
        question=request.question,
        title_filter=request.title_filter
    )
    
    # Защита от None
    safe_answer = str(response.response or "Не удалось сгенерировать ответ.")
    safe_sources = len(response.source_nodes or [])
    
    # Собираем заголовки источников
    matched_titles = []
    for node in (response.source_nodes or []):
        t = node.metadata.get("document_title", "unknown")
        if t not in matched_titles:
            matched_titles.append(t)
    
    # Определяем уверенность
    confidence = "low"
    if response.source_nodes:
        best_score = response.source_nodes[0].score
        if best_score >= CONFIDENCE_THRESHOLD:
            confidence = "high"
    
    return AnswerResponse(
        answer=safe_answer,
        sources_count=safe_sources,
        matched_titles=matched_titles,
        confidence=confidence
    )