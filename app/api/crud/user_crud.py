from sqlalchemy.orm import Session
from app.db.models import Card, User, ConnectedProvider, ConnectedProvider


from app.utils.security import verify_password
def delete_user_account(db: Session, user_id: int, password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user and verify_password(password, user.hashed_password):
        # Delete related data first (assuming cascading delete is not set up)
        db.query(Card).filter(Card.user_id == user_id).delete()
        db.query(ConnectedProvider).filter(ConnectedProvider.user_id == user_id).delete()
        
        # Delete the user
        db.delete(user)
        db.commit()
        return True
    return False