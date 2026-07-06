"""Chat endpoint — Gemini-powered follow-up Q&A.

Uses Gemini 2.0 Flash for intelligent responses. Falls back to keyword
pattern matching when Gemini is unavailable.
"""

from fastapi import APIRouter

from app.api.schemas.recommendation import ChatRequest, ChatResponse
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/chat", tags=["chat"])

_gemini = GeminiService()


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = _gemini.chat(req.question, req.context)
    return ChatResponse(answer=result["answer"], citations=result["citations"])
