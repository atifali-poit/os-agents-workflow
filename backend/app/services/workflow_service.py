from sqlalchemy.orm import Session

from app.models import Workflow


def list_workflows(db: Session) -> list[Workflow]:
    return db.query(Workflow).order_by(Workflow.id).all()

