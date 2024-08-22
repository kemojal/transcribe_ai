from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.schemas import UserCreate
from app.api.crud import provider_crud, card_crud
# from ..models.users import User as UserSchema, UserCreate, UserUpdate, UserRegisterSchema, UserLoginSchema
from ...db.database import get_db
from app.db.models import User
# from app.api.models.users import UserResponse
from app.api.models.schemas import UserResponse, UserLoginSchema, UserUpdate, ConnectedProviders, Message, ProviderDisconnect, ProviderConnect, CardCreate, CardUpdate, CardList, Card, CardCreate, CardUpdate
from ...utils.security import get_password_hash, verify_password, get_current_user, create_access_token, create_refresh_token, verify_refresh_token, validate_token

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# @router.post("/register")
# def register_user(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
#     # Implement user registration logic here

#     return [{"username": "Rick"}, {"username": "Morty"}]

#     pass

# @router.post("/login")
# def login_user(user_data: UserLoginSchema, db: Session = Depends(get_db)):
#     # Implement user login logic here
#     pass

# # Add other user-related routes as needed
# @router.post("/register", response_model=UserRegisterSchema)
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=password_hash, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login_user(user_credentials: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate and return an access token
    access_token = create_access_token(data={"user_id": user.id})
    # Generate refresh token
    refresh_token = create_refresh_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.get("/validate_token")
async def validate_token_endpoint(token: str):
    # Replace with your actual token validation logic
    return await validate_token(token)


# Implement a token refresh endpoint
@router.post("/refresh-token")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    # Verify the refresh token
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Generate a new access token
    access_token = create_access_token(data={"user_id": user_id})

    return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/{user_id}", response_model=UserSchema)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if the user_id matches the current logged-in user's id
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # print("current user = ", current_user.id)
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    if update_data.get("password"):
        password_hash = get_password_hash(update_data["password"])
        update_data["password_hash"] = password_hash
        del update_data["password"]
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/connected-provider", response_model=ConnectedProviders)
def read_connected_providers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    providers = provider_crud.get_connected_providers(db, current_user.id)
    return {"providers": providers}

@router.post("/connect-provider", response_model=Message)
def connect_provider(
    provider: ProviderConnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if provider_crud.connect_provider(db, current_user.id, provider.provider):
        return {"message": f"Successfully connected {provider.provider}"}
    raise HTTPException(status_code=400, detail="Failed to connect provider")

@router.post("/disconnect-provider", response_model=Message)
def disconnect_provider(
    provider: ProviderDisconnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if provider_crud.disconnect_provider(db, current_user.id, provider.provider):
        return {"message": f"Successfully disconnected {provider.provider}"}
    raise HTTPException(status_code=400, detail="Failed to disconnect provider")



# cards
@router.get("/cards", response_model=CardList)
def read_user_cards(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    print("current_user.id  = ",  current_user.id)
    cards = card_crud.get_user_cards(db, current_user.id)
    return {"cards": cards}

@router.post("/cards", response_model=Card)
def create_card(card: CardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return card_crud.create_user_card(db, card, current_user.id)

@router.put("/cards/{card_id}", response_model=Card)
def update_card(card_id: int, card: CardUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_card = card_crud.update_user_card(db, card_id, card, current_user.id)
    if updated_card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return updated_card

@router.delete("/cards/{card_id}", response_model=Message)
def delete_card(card_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if card_crud.delete_user_card(db, card_id, current_user.id):
        return {"message": "Card successfully deleted"}
    raise HTTPException(status_code=404, detail="Card not found")