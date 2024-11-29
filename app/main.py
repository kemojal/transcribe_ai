import cloudinary
import os 
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from moviepy.editor import VideoClip, TextClip, CompositeVideoClip
import numpy as np
from PIL import ImageFont

# from app.websocket_manager import app as websocket_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.models.schemas import RenderRequest
from app.utils.helpers import create_text_clip, parse_timestamp





from .api import api_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add the logging middleware
# app.add_middleware(LoggingMiddleware)


# print("GEMNI_API_KEY", os.environ["GEMNI_API_KEY"])
# import google.generativeai as genai
# import os
# genai.configure(api_key=os.environ["GEMNI_API_KEY"])

# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("Write a story about a magic backpack.")
# print("response AI=", response.text)



origins = [
   
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "https://editube-kemojals-projects.vercel.app",
    "http://localhost:5173/"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



load_dotenv()
          
# cloudinary.config( 
#   cloud_name = "dtpnbesbx", 
#   api_key = "811133693665998", 
#   api_secret = "1YJOBmJ9LN1Aqhyc8AlUoAOHF9A" 
# )
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET") 
)

app.include_router(api_router)

# Include the WebSocket app
# app.mount("/", websocket_app)

@app.get("/")
async def read_item():
    return {"hello word"}



def create_text_clip(entry, style, video_size):
    # Create the TextClip using moviepy
    text_clip = TextClip(
        entry.content,
        font=style.font_family,
        fontsize=style.font_size,
        color=style.color
    ).set_position(('center', 'bottom')).set_duration(entry.timestamp_end - entry.timestamp_start)
    
    return text_clip


# @app.post("/render")
# async def render_video(request: RenderRequest):
#     try:
#         video_size = (720, 1280)  # Set video size for vertical video (aspect ratio 9:16)

#         # Create a blank video clip (black background, 30 seconds long)
#         def make_frame(t):
#             return np.zeros((video_size[1], video_size[0], 3), dtype=np.uint8)  # Black frame (720x1280 video size)
        
#         video_clip = VideoClip(make_frame, duration=30).set_duration(30).set_fps(24).resize(video_size)
        
#         # List to store the text clips
#         text_clips = []

#         # Create text clips for each entry
#         for entry in request.entries:
#             text_clip = create_text_clip(entry, request.text_style, video_size)
#             text_clip = text_clip.set_start(entry.timestamp_start)  # Add the start time to the clip
#             text_clips.append(text_clip)

#         # If you need to manipulate images with Pillow
#         # Example: Open and resize an image
#         image = Image.open('path_to_image.jpg')
#         resized_image = image.resize((720, 1280), Image.Resampling.LANCZOS)
#         resized_image.save('resized_image.jpg')

#         # Overlay the text clips on the blank video
#         final_clip = CompositeVideoClip([video_clip] + text_clips)

#         # Set the output file path
#         output_path = os.path.join(os.getcwd(), "out", "transcription-video.mp4")

#         # Write the final video to a file
#         final_clip.write_videofile(output_path, fps=24)

#         return {"output_location": output_path}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)





@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )