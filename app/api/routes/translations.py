from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

from app.db.database import get_db
from app.utils.security import get_current_user
from app.db.models import Translation, Subtitle
from app.api.models.schemas import TranslationCreate, TranslationResponse, UserResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.environ["GEMNI_API_KEY"])
gemni_model = genai.GenerativeModel("gemini-1.5-flash")

router = APIRouter(
    prefix="/subtitles/{subtitle_id}/translations",
    tags=["Translations"],
)

def translate_text(text: str, target_language: str) -> str:
    """
    Translate text using Gemini AI
    """
    try:
        prompt = f"Translate the following text to {target_language}. Maintain the same format and structure. Here's the text:\n\n{text}"
        response = gemni_model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty translation received from Gemini AI")
            
        return response.text.strip()
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@router.post("/", response_model=TranslationResponse)
async def create_translation(
    subtitle_id: int,
    translation: TranslationCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    # Check if subtitle exists
    subtitle = db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()
    if not subtitle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtitle not found"
        )
    
    # Check if translation in this language already exists
    existing_translation = db.query(Translation).filter(
        Translation.subtitle_id == subtitle_id,
        Translation.language_code == translation.language_code
    ).first()
    
    if existing_translation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Translation in {translation.language_code} already exists"
        )

    try:
        # Translate the subtitle text
        translated_text = translate_text(
            subtitle.subtitle_text,
            translation.language_code
        )
        
        # Create new translation entry
        db_translation = Translation(
            subtitle_id=subtitle_id,
            language_code=translation.language_code,
            translated_text=translated_text
        )
        
        db.add(db_translation)
        db.commit()
        db.refresh(db_translation)
        
        return db_translation
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{translation_id}", response_model=TranslationResponse)
async def get_translation(
    subtitle_id: int,
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.subtitle_id == subtitle_id
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    return translation

@router.get("/", response_model=list[TranslationResponse])
async def list_translations(
    subtitle_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    translations = db.query(Translation).filter(
        Translation.subtitle_id == subtitle_id
    ).all()
    
    return translations
