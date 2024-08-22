from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserUpdate(UserCreate):
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



class UserBase(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

# Project and file schemas
class TranscriptionResponse(BaseModel):
    id: int
    # original_filename: str
    transcription_text: Optional[str]
    language: Optional[str]
    # user_id: int

    class Config:
        orm_mode = True

class FileBase(BaseModel):
    name: str
    path: str

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    project_id: int
    public_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    transcriptions: List[TranscriptionResponse] = []

    class Config:
        orm_mode = True



class FileSchema(BaseModel):
    name: str
    path: str

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    user: UserBase
    created_at: datetime
    updated_at: Optional[datetime]
    files: List[FileResponse] = []
    transcriptions: List[TranscriptionResponse] = []

    class Config:
        orm_mode = True

# Subtitle schemas
class SubtitleCreate(BaseModel):
    transcription_id: int
    subtitle_format: str

class SubtitleResponse(BaseModel):
    id: int
    subtitle_format: str
    subtitle_text: Optional[str]
    created_at: str

    class Config:
        orm_mode = True

# Translation schemas
class TranslationCreate(BaseModel):
    subtitle_id: int
    language_code: str

class TranslationResponse(BaseModel):
    id: int
    language_code: str
    translated_text: Optional[str]
    created_at: str

    class Config:
        orm_mode = True

# Update forward references
FileResponse.update_forward_refs()
ProjectResponse.update_forward_refs()



# chatgpt models
class TranscriptionRequest(BaseModel):
    transcription_text: str

class SummarizationResponse(BaseModel):
    summary: str

class CaptionEnhancementRequest(BaseModel):
    subtitle_text: str

class EnhancedCaptionResponse(BaseModel):
    enhanced_subtitles: str

class QnARequest(BaseModel):
    question: str
    transcription_text: str

class QnAResponse(BaseModel):
    answer: str

class CaptionGenerationRequest(BaseModel):
    transcription_text: str
    style: str

class CaptionGenerationResponse(BaseModel):
    captions: str

class SentimentAnalysisResponse(BaseModel):
    sentiment: str
    insights: str

class TranslationRequest(BaseModel):
    transcription_text: str
    target_language: str

class TranslationResponseB(BaseModel):
    translated_text: str


class TokenRequest(BaseModel):
    token: str



class ProviderConnect(BaseModel):
    provider: str

class ProviderDisconnect(BaseModel):
    provider: str

class ConnectedProviders(BaseModel):
    providers: List[str]

class Message(BaseModel):
    message: str



#cards

class CardBase(BaseModel):
    last_four: str
    brand: str
    exp_month: int
    exp_year: int

class CardCreate(CardBase):
    token: str  # This would be a token from a payment processor like Stripe

class CardUpdate(CardBase):
    pass

class Card(CardBase):
    id: int
    is_default: bool

    class Config:
        orm_mode = True

class CardList(BaseModel):
    cards: List[Card]