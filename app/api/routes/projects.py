

import whisper
# from stable_whisper import timestamped_transcription
import stable_whisper


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db.database import get_db
# from app.db.models import Project, ProjectCollaborator, User
# from app.api.models.projects import ProjectCreate, ProjectUpdate, CollaboratorEmailList, ProjectResponse, UserResponse
from app.utils.security import get_current_user
# from app.utils.email import send_invitation_email

from app.api.models.schemas import  ProjectResponse, ProjectCreate
from app.db.models import Project

# from app.db.models import Transcription
from app.api.models.schemas import  UserResponse
# from app import models, schemas



logger = logging.getLogger(__name__)  # Define or import logger

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)



# Create a project
@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_project = Project(name=project.name
    # , description=project.description
    , user_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

    # return crud.create_project(db=db, project=project, user_id=current_user.id)

# Get all projects for a user
@router.get("/", response_model=List[ProjectResponse])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    created_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return created_projects

# Get a specific project by ID
@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    # db_project = crud.get_project(db, project_id=project_id)
    db_project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project



@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    update_data = project.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project




@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}



# # Upload a file to a project
# @router.post("/projects/{project_id}/files/", response_model=schemas.File)
# def create_file(project_id: int, file: FastAPIFile = File(...), db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     db_project = crud.get_project(db, project_id=project_id)
#     if db_project is None or db_project.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Project not found")

#     file_location = f"files/{file.filename}"
#     with open(file_location, "wb+") as file_object:
#         shutil.copyfileobj(file.file, file_object)

#     file_create = schemas.FileCreate(filename=file.filename, filepath=file_location)
#     return crud.create_file(db=db, file=file_create, project_id=project_id)

# # Get all files for a project
# @router.get("/projects/{project_id}/files/", response_model=List[schemas.File])
# def read_files(project_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     db_project = crud.get_project(db, project_id=project_id)
#     if db_project is None or db_project.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Project not found")

#     return crud.get_files(db=db, project_id=project_id)

# # Get a specific file by ID
# @router.get("/projects/{project_id}/files/{file_id}", response_model=schemas.File)
# def read_file(project_id: int, file_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     db_project = crud.get_project(db, project_id=project_id)
#     if db_project is None or db_project.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Project not found")

#     db_file = crud.get_file(db=db, file_id=file_id)
#     if db_file is None:
#         raise HTTPException(status_code=404, detail="File not found")
    
#     return db_file
