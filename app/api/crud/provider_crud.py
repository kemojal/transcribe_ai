
from sqlalchemy.orm import Session
from app.db.models import  ConnectedProvider, ConnectedProvider, ConnectedProvider
# from app.api.models.schemas import  
def get_connected_providers(db: Session, user_id: int):
    return [cp.provider for cp in db.query(ConnectedProvider).filter(ConnectedProvider.user_id == user_id).all()]

def connect_provider(db: Session, user_id: int, provider: str):
    db_provider = ConnectedProvider(user_id=user_id, provider=provider)
    db.add(db_provider)
    try:
        db.commit()
        return True
    except:
        db.rollback()
        return False

def disconnect_provider(db: Session, user_id: int, provider: str):
    db_provider = db.query(models.ConnectedProvider).filter(
        models.ConnectedProvider.user_id == user_id,
        models.ConnectedProvider.provider == provider
    ).first()
    if db_provider:
        db.delete(db_provider)
        db.commit()
        return True
    return False