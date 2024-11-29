from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.utils.security import get_current_user
from app.api.models.schemas import FileResponse, UserResponse
from app.db.models import File, Project

router = APIRouter(
    prefix="/user/files",
    tags=["User_Files"]
)

# # Get all files across all projects for the current user
# @router.get("/files", response_model=List[FileResponse])
# def get_all_files_for_user(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     # Efficient single query to fetch files from all projects owned by the user
#     files = db.query(File).join(Project).filter(Project.user_id == current_user.id).all()
#     return files

@router.get("", response_model=List[FileResponse])
def get_all_files_for_user(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    # Step 1: Get all projects owned by the user
    user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    
    if not user_projects:
        return []

    # Step 2: Collect all files associated with the user's projects
    all_files = []
    for project in user_projects:
        project_files = db.query(File).filter(File.project_id == project.id).all()
        all_files.extend(project_files)

    return all_files

