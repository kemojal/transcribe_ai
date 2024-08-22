from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils import get_current_user

router = APIRouter(
    prefix='/subtitles',
    tags=['Subtitles'],
)

@router.post("/", response_model=schemas.SubtitleResponse)
def create_subtitle(subtitle: schemas.SubtitleCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    transcription = db.query(models.Transcription).filter(models.Transcription.id == subtitle.transcription_id, models.Transcription.user_id == current_user.id).first()
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
    
    # Generate subtitle text using Stable-TS
    subtitle_text = "Generated subtitle text"

    new_subtitle = models.Subtitle(transcription_id=subtitle.transcription_id, subtitle_format=subtitle.subtitle_format, subtitle_text=subtitle_text)
    db.add(new_subtitle)
    db.commit()
    db.refresh(new_subtitle)
    return new_subtitle

@router.get("/{id}", response_model=schemas.SubtitleResponse)
def get_subtitle(id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    subtitle = db.query(models.Subtitle).filter(models.Subtitle.id == id).first()
    if not subtitle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtitle not found")
    return subtitle

@router.get("/", response_model=list[schemas.SubtitleResponse])
def list_subtitles(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    subtitles = db.query(models.Subtitle).join(models.Transcription).filter(models.Transcription.user_id == current_user.id).all()
    return subtitles

@router.delete("/{id}")
def delete_subtitle(id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    subtitle = db.query(models.Subtitle).join(models.Transcription).filter(models.Subtitle.id == id, models.Transcription.user_id == current_user.id).first()
    if not subtitle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtitle not found")
    db.delete(subtitle)
    db.commit()
    return {"message": "Subtitle deleted"}
