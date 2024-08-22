from sqlalchemy.orm import Session
from app.db.models import Project, File, Transcription
from app.api.models.schemas import ProjectCreate, FileCreate, TranslationResponse, FileSchema

def create_project(db: Session, project: ProjectCreate, user_id: int):
    db_project = Project(name=project.name, user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.user_id == user_id).all()

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def create_file(db: Session, file: FileSchema, project_id: int):
    db_file = File(name=file.name,path=file.path, project_id=project_id, public_id=file.public_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files(db: Session, project_id: int):
    return db.query(File).filter(File.project_id == project_id).all()

def get_file(db: Session, file_id: int):
    return db.query(File).filter(File.id == file_id).first()


def delete_file(db: Session, file_id: int):
    db.query(File).filter(File.id == file_id).delete()
    db.commit()

def create_transcription(db: Session, transcription: TranslationResponse, project_id: int, file_id: int):
    db_transcription = Transcription(text=transcription.text, project_id=project_id, file_id=file_id)
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    return db_transcription

def get_transcriptions(db: Session, project_id: int):
    return db.query(Transcription).filter(Transcription.project_id == project_id).all()

def get_transcription(db: Session, transcription_id: int):
    return db.query(Transcription).filter(Transcription.id == transcription_id).first()
