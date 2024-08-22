from fastapi import APIRouter, Depends, UploadFile,File, HTTPException, status
from sqlalchemy.orm import Session
# from app import models, schemas
from app.db.database import get_db
from app.utils.security import get_current_user


import cloudinary


from dotenv import load_dotenv
load_dotenv()

import cloudinary.uploader
import cloudinary.api

from app.api.models.schemas  import   FileResponse, FileSchema

from typing import List

from app.api.models.schemas import  UserResponse
from app.api.crud import project_crud

from app.db.models import File as FileModel

router = APIRouter(
    prefix="/projects/{project_id}",
    tags=["Files"],
)



# Configure Cloudinary
cloudinary.config(
    cloud_name='dtpnbesbx',
    api_key='811133693665998',
    api_secret='1YJOBmJ9LN1Aqhyc8AlUoAOHF9A'
)
config = cloudinary.config(secure=True)
print("****1. Set up and configure the SDK:****\nCredentials: ", config.cloud_name, config.api_key, "\n")



# Upload a file to a project
@router.post("/files", response_model=FileResponse)
def upload_file(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):

    db_project = project_crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    

    try:
        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(file.file, resource_type="video", display_name=file.filename, folder=f"files/{project_id}")
        print("result xx = ", result)
        file_url = result.get('secure_url')
        file_public_id = result.get('public_id')

        # Save file details to the database
        file_create = FileModel(name=file.filename, path=file_url, public_id=file_public_id)
        created_file = project_crud.create_file(db=db, file=file_create, project_id=project_id)
        
        return created_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    project_id: int, 
    file_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    db_project = project_crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_file = project_crud.get_file(db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete the file from Cloudinary
        cloudinary.uploader.destroy(db_file.public_id, resource_type="video")
        
        # Delete the file record from the database
        project_crud.delete_file(db=db, file_id=file_id)
        # db.query(File).filter(File.id == file_id).delete()
        # db.commit()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get all files for a project
@router.get("/files", response_model=List[FileResponse])
def read_files(project_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_project = project_crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    return project_crud.get_files(db=db, project_id=project_id)


# Get a specific file by ID
@router.get("/files/{file_id}", response_model=FileResponse)
def read_file(project_id: int, file_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_project = project_crud.get_project(db, project_id=project_id)
    if db_project is None or db_project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    db_file = project_crud.get_file(db=db, file_id=file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return db_file



@router.get("/{id}/download")
def download_file(id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    file = db.query(File).filter(File.id == id, File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return {"file_path": file.file_path}  # Adjust as needed for actual file download

@router.delete("/{id}")
def delete_file(id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    file = db.query(File).filter(File.id == id, File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    db.delete(file)
    db.commit()
    return {"message": "File deleted"}
