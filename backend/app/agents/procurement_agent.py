from sqlalchemy.orm import Session

from app.services.runtime_engine import RuntimeEngine


class ProcurementAgent:
    name = "ProcurementAgent"

    def run(self, db: Session):
        return RuntimeEngine(db).execute("vendor", triggered_by="procurement_agent")
