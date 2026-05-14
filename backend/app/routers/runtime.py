from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.runtime_engine import RuntimeEngine
from app.schemas import RuntimeRequest, RuntimeSummary

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


@router.post("/execute", response_model=RuntimeSummary)
def execute_runtime(request: RuntimeRequest, db: Session = Depends(get_db)):
    return RuntimeEngine(db).execute(request.entity_type)
