from sqlalchemy.orm import Session

from app.services.runtime_engine import RuntimeEngine


class HRAgent:
    name = "HRAgent"

    def run(self, db: Session):
        return RuntimeEngine(db).execute("leave", triggered_by="hr_agent")
