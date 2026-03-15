from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.models.document import Document
from app.models.team import Team
from app.schemas.document import DocumentImportRequest


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def import_document(self, payload: DocumentImportRequest) -> Document:
        team = self.db.get(Team, payload.team_id)
        if team is None:
            raise EntityNotFoundError(f"Team '{payload.team_id}' does not exist.")

        document = Document(
            document_id=str(uuid4()),
            team_id=payload.team_id,
            source_name=payload.source_name,
            content_type=payload.content_type,
            content=payload.content,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_documents(self, team_id: str) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.team_id == team_id)
            .order_by(Document.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_document_in_team(self, document_id: str, team_id: str) -> Document:
        stmt = select(Document).where(
            Document.document_id == document_id,
            Document.team_id == team_id,
        )
        document = self.db.scalar(stmt)
        if document is None:
            raise EntityNotFoundError(
                f"Document '{document_id}' not found in team '{team_id}'."
            )

        return document