from sqlalchemy.orm import Session

from app.db.models import  Card
from app.api.models.schemas import  CardCreate, CardUpdate

def get_user_cards(db: Session, user_id: int):
    # return db.query(Card).filter(Card.user_id == user_id).all()
    return db.query(Card).filter(Card.user_id == user_id).all()

def create_user_card(db: Session, card: CardCreate, user_id: int):
    db_card = Card(**card.dict(), user_id=user_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

def update_user_card(db: Session, card_id: int, card: CardUpdate, user_id: int):
    db_card = db.query(Card).filter(Card.id == card_id, Card.user_id == user_id).first()
    if db_card:
        for key, value in card.dict().items():
            setattr(db_card, key, value)
        db.commit()
        db.refresh(db_card)
    return db_card

def delete_user_card(db: Session, card_id: int, user_id: int):
    db_card = db.query(Card).filter(Card.id == card_id, Card.user_id == user_id).first()
    if db_card:
        db.delete(db_card)
        db.commit()
        return True
    return False