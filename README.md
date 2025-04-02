# Transcribe AI

A powerful FastAPI-based application for audio transcription, summarization, and analysis using state-of-the-art AI models.

## Features

- **Audio Transcription**: Convert audio files to text using OpenAI's Whisper model
- **Speaker Diarization**: Identify and separate different speakers in audio files
- **Multi-language Support**: Transcribe and process audio in multiple languages
- **AI-powered Summarization**: Generate concise summaries of transcriptions
- **Caption Enhancement**: Improve and format captions for better readability
- **Cloud Storage Integration**: Store and manage files using Cloudinary
- **Database Management**: SQLAlchemy-based database for storing transcriptions and metadata
- **RESTful API**: FastAPI-based endpoints for all transcription services
- **WebSocket Support**: Real-time communication capabilities

## Tech Stack

- **Backend**: FastAPI, Python 3.12+
- **Database**: SQLAlchemy, Alembic (for migrations)
- **AI Models**:
  - OpenAI Whisper (transcription)
  - OpenAI GPT (summarization)
  - Google Gemini (enhanced summarization)
  - Pyannote (speaker diarization)
- **File Storage**: Cloudinary
- **Authentication**: JWT-based authentication
- **WebSockets**: For real-time features

## Prerequisites

- Python 3.12 or higher
- FFmpeg (for audio processing)
- Git
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/kemojal/transcribe_ai.git
cd transcribe_ai
```

2. Create and activate a virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
HF_TOKEN=your_huggingface_token_here
GEMNI_API_KEY=your_gemini_api_key_here
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
CLOUDINARY_URL=your_cloudinary_url
```

## Running the Application

1. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

2. Access the API documentation at:

```
http://localhost:8000/docs
```

## API Endpoints

### Transcriptions

- `POST /projects/{project_id}/files/{file_id}/transcriptions`: Create a new transcription
- `GET /projects/{project_id}/files/{file_id}/transcriptions/{id}`: Get a specific transcription
- `GET /projects/{project_id}/files/{file_id}/transcriptions`: List all transcriptions
- `PUT /projects/{project_id}/files/{file_id}/transcriptions/{id}`: Update a transcription
- `DELETE /projects/{project_id}/files/{file_id}/transcriptions/{id}`: Delete a transcription

### Additional Features

- `POST /{id}/summarize-transcription`: Generate a summary of a transcription
- `POST /{id}/enhance-captions`: Enhance and format captions
- `POST /{id}/ask-chatgpt`: Ask questions about the transcription
- `POST /{id}/generate-stylized-captions`: Generate captions in different styles
- `POST /{id}/analyze-sentiment`: Analyze sentiment of the transcription
- `POST /{id}/translate-transcription`: Translate transcription to another language

## Project Structure

```
transcribe_ai/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── crud/
│   ├── db/
│   │   ├── models/
│   │   └── database.py
│   ├── utils/
│   └── main.py
├── alembic/
├── tests/
├── requirements.txt
└── .env
```

## Security Considerations

- API keys and sensitive information are stored in environment variables
- JWT-based authentication for API endpoints
- Input validation and sanitization
- Rate limiting and request validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the Whisper model
- Hugging Face for the Pyannote library
- Google for the Gemini model
- FastAPI team for the excellent framework
