from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils import get_current_user

router = APIRouter(
    prefix='/translations',
    tags=['Translations'],
)

@router.post("/", response_model=schemas.TranslationResponse)
def create_translation(translation: schemas.TranslationCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    subtitle = db.query(models.Subtitle).join(models.Transcription).filter(models.Subtitle.id == translation.subtitle_id, models.Transcription.user_id == current_user.id).first()
    if not subtitle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtitle not found")
    
    # Translate subtitle text
    translated_text = "Translated text"

    new_translation = models.Translation(subtitle_id=translation.subtitle_id, language_code=translation.language_code, translated_text=translated_text)
    db.add(new_translation)
    db.commit()
    db.refresh(new_translation)
    return new_translation

@router.get("/{id}", response_model=schemas.TranslationResponse)
def get_translation(id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    translation = db.query(models.Translation).join(models.Subtitle).join(models.Transcription).filter(models.Translation.id == id, models.Transcription.user_id == current_user.id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")
    return translation

@router.get("/", response_model=list[schemas.TranslationResponse])
def list_translations(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    translations = db.query(models.Translation).join(models.Subtitle).join(models.Transcription).filter(models.Transcription.user_id == current_user.id).all()
    return translations

@router.delete("/{id}")
def delete_translation(id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    translation = db.query(models.Translation).join(models.Subtitle).join(models.Transcription).filter(models.Translation.id == id, models.Transcription.user_id == current_user.id).first()
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")
    db.delete(translation)
    db.commit()
    return {"message": "Translation deleted"}
