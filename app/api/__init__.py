from fastapi import APIRouter

from .routes import users, transcriptions, projects, files, google
# projects, videos, comments, notifications, activity_feeds, upload, annotations
# , 
# analytics
# google_account_integration

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(transcriptions.router)
api_router.include_router(projects.router)
api_router.include_router(files.router)
api_router.include_router(google.router)
# api_router.include_router(videos.router)
# api_router.include_router(comments.router)
# api_router.include_router(notifications.router)
# api_router.include_router(activity_feeds.router)
# api_router.include_router(upload.router)
# api_router.include_router(annotations.router)

