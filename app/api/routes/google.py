from fastapi import APIRouter, Depends, UploadFile,File, HTTPException, status
from sqlalchemy.orm import Session
# from app import models, schemas
from app.db.database import get_db
from jose import jwt,  JWTError
from fastapi.security import OAuth2PasswordBearer


from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.transport.requests import Request


import logging

import requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from app.db.models import User
from app.api.models.schemas import TokenRequest


from ...utils.security import create_access_token, create_refresh_token, verify_refresh_token



# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = "904368645947-eqsu94el8hurjna34ah19dnumec4kk5h.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://localhost:8000"


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# @router.get("/one/login/google")
# async def login_google():
#     return {
#         "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
#     }

# @router.get("/auth/google")
# async def auth_google(code: str):
#     token_url = "https://accounts.google.com/o/oauth2/token"
#     data = {
#         "code": code,
#         "client_id": GOOGLE_CLIENT_ID,
#         "client_secret": GOOGLE_CLIENT_SECRET,
#         "redirect_uri": GOOGLE_REDIRECT_URI,
#         "grant_type": "authorization_code",
#     }
#     response = requests.post(token_url, data=data)
#     access_token = response.json().get("access_token")
#     user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
#     return user_info.json()

# @router.get("/token")
# async def get_token(token: str = Depends(oauth2_scheme)):
#     return jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])




@router.get("/login/google")
async def google_auth(token: str, db: Session = Depends(get_db)):
    
    try:
        # Verify Google OAuth2 token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        google_user_id = idinfo["sub"]
        email = idinfo["email"]
        username = idinfo.get("name")

        print("google user id", google_user_id)

        # Check if user exists
        user = db.query(User).filter(User.oauth_provider_id == google_user_id).first()

        if not user:
            # Create a new user if not found
            user = User(
                email=email,
                username=username,
                oauth_provider="google",
                oauth_provider_id=google_user_id,
            )
            db.add(user)
            db.commit()

        # Optionally create a session/token here
        return {"message": "Login successful", "user": {"id": user.id, "email": user.email}}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")


@router.post("/auth/google")
async def google_auth_signup(payload: TokenRequest, db: Session = Depends(get_db)):
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(payload.token, Request(), GOOGLE_CLIENT_ID)
        logging.debug("Google token = %s", idinfo["sub"])

        # Extract user information from token
        google_user_id = idinfo["sub"]
        email = idinfo["email"]
        username = idinfo.get("name", email.split('@')[0])  # Fallback to email username if name not provided
        logging.debug("Google account email: %s, %s", google_user_id, username)

        # Check if the user already exists in the database
        user = db.query(User).filter(User.oauth_provider_id == google_user_id).first()

        if not user:
            # If user does not exist, create a new one
            user = User(
                email=email,
                username=username,
                oauth_provider="google",
                oauth_provider_id=google_user_id,
                password_hash=""  # Assuming it's required even though it may be empty for OAuth users
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate and return an access token
        access_token = create_access_token(data={"user_id": user.id})
        # Generate refresh token
        refresh_token = create_refresh_token(data={"user_id": user.id})

        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
        

    except ValueError as ve:
        logging.error("ValueError: %s", ve)
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        logging.error("Exception: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")