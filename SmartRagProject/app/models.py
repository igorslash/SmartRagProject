from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    title_filter: str = ""


class AnswerResponse(BaseModel):
    answer: str
    sources_count: int
    matched_titles: list[str]
    confidence: str  