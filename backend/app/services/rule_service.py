from sqlalchemy.orm import Session

from app.models import Rule
from app.schemas import RuleCreate


def list_rules(db: Session) -> list[Rule]:
    return db.query(Rule).order_by(Rule.id).all()


def create_rule(db: Session, rule_in: RuleCreate) -> Rule:
    rule_data = rule_in.model_dump()
    rule_data["enabled"] = True if rule_data.get("enabled") is None else rule_data["enabled"]
    rule = Rule(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
