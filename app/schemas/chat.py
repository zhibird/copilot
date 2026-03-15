from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.schemas.retrieval import RetrievalHit


class ChatEchoRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    team_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2000)


class ChatEchoResponse(BaseModel):
    user_id: str
    team_id: str
    answer: str
    created_at: str

    @classmethod
    def from_message(cls, user_id: str, team_id: str, answer: str) -> "ChatEchoResponse":
        return cls(
            user_id=user_id,
            team_id=team_id,
            answer=answer,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class ChatAskRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    team_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_id: str | None = Field(default=None, min_length=1, max_length=36)


class ChatAskResponse(BaseModel):
    user_id: str
    team_id: str
    question: str
    answer: str
    hits: list[RetrievalHit]
    created_at: str

    @classmethod
    def from_result(
        cls,
        user_id: str,
        team_id: str,
        question: str,
        answer: str,
        hits: list[RetrievalHit],
    ) -> "ChatAskResponse":
        return cls(
            user_id=user_id,
            team_id=team_id,
            question=question,
            answer=answer,
            hits=hits,
            created_at=datetime.now(timezone.utc).isoformat(),
        )