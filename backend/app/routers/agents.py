from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents import FinanceAgent, HRAgent, ProcurementAgent
from app.database import get_db
from app.schemas import RuntimeSummary

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/finance/run", response_model=RuntimeSummary)
def run_finance_agent(db: Session = Depends(get_db)):
    return FinanceAgent().run(db)


@router.post("/procurement/run", response_model=RuntimeSummary)
def run_procurement_agent(db: Session = Depends(get_db)):
    return ProcurementAgent().run(db)


@router.post("/hr/run", response_model=RuntimeSummary)
def run_hr_agent(db: Session = Depends(get_db)):
    return HRAgent().run(db)

