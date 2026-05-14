from sqlalchemy.orm import Session

from app.services.runtime_engine import RuntimeEngine


class FinanceAgent:
    name = "FinanceAgent"

    def run(self, db: Session):
        return RuntimeEngine(db).execute("invoice", triggered_by="finance_agent")
