from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Rule
from app.schemas import RuleCreate, RuleOut, RuleUpdate, TranslateRequest, TranslateResponse
from app.services.ai_translation_service import translate_prompt
from app.services.rule_service import create_rule, list_rules

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("", response_model=list[RuleOut])
def get_rules(db: Session = Depends(get_db)):
    return list_rules(db)


@router.post("", response_model=RuleOut)
def post_rule(rule_in: RuleCreate, db: Session = Depends(get_db)):
    return create_rule(db, rule_in)


@router.put("/{rule_id}", response_model=RuleOut)
def put_rule(rule_id: int, rule_in: RuleUpdate, db: Session = Depends(get_db)):
    rule = db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in rule_in.model_dump().items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/{rule_id}/toggle", response_model=RuleOut)
def toggle_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.get(Rule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.enabled = not rule.enabled
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/translate", response_model=TranslateResponse)
def translate_rule(request: TranslateRequest):
    try:
        return translate_prompt(request.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
