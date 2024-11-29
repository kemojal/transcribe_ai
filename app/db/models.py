from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(Text, nullable=True)
    oauth_provider = Column(String, nullable=True)  # Add this field
    oauth_provider_id = Column(String, unique=True, nullable=True)  # Add this field
    created_at = Column(TIMESTAMP, server_default=func.now())

    connected_providers = relationship("ConnectedProvider", back_populates="user")
    cards = relationship("Card", back_populates="user")



class ConnectedProvider(Base):
    __tablename__ = "connected_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String)

    user = relationship("User", back_populates="connected_providers")


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    files = relationship("File", back_populates="project")
    transcriptions = relationship("Transcription", back_populates="project")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    file_type = Column(String)
    path = Column(Text)
    public_id = Column(String, index=True) 
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # user = relationship("User")


    project = relationship("Project", back_populates="files")
    transcriptions = relationship("Transcription", back_populates="file")

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # original_filename = Column(String)
    project_id = Column(Integer, ForeignKey('projects.id'))
    file_id = Column(Integer, ForeignKey('files.id'))
    transcription_text = Column(Text, nullable=True)
    language = Column(String(50))
    summary_text = Column(Text, nullable=True)  # Summarized version
    repurposed_text = Column(Text, nullable=True) # Repurposed content, e.g., video script, tweet, etc.
    # created_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="transcriptions")
    file = relationship("File", back_populates="transcriptions")


    # user = relationship("User")

User.projects = relationship("Project", back_populates="user")
Project.files = relationship("File", back_populates="project")
Project.transcriptions = relationship("Transcription", back_populates="project")
File.transcriptions = relationship("Transcription", back_populates="file")


class Subtitle(Base):
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id", ondelete="CASCADE"))
    subtitle_format = Column(String)
    subtitle_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    transcription = relationship("Transcription")

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id", ondelete="CASCADE"))
    language_code = Column(String)
    translated_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    subtitle = relationship("Subtitle")




class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    last_four = Column(String(4))
    brand = Column(String)
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="cards")