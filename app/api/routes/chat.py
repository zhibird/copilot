from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_service, get_rag_chat_service
from app.core.exceptions import DomainValidationError, EntityNotFoundError
from app.schemas.chat import ChatAskRequest, ChatAskResponse, ChatEchoRequest, ChatEchoResponse
from app.services.chat_service import ChatService
from app.services.rag_chat_service import RagChatService

router = APIRouter(prefix="/chat")


@router.post("/echo", response_model=ChatEchoResponse)
def chat_echo(
    payload: ChatEchoRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatEchoResponse:
    try:
        return chat_service.echo(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/ask", response_model=ChatAskResponse)
def chat_ask(
    payload: ChatAskRequest,
    rag_chat_service: RagChatService = Depends(get_rag_chat_service),
) -> ChatAskResponse:
    try:
        return rag_chat_service.ask(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc