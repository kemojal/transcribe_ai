import whisper
# from pyannote.audio import Pipeline

##Initialize the pipeline globally
# pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
# print("Pipeline initialized:", pipeline)

import requests
# from stable_whisper import timestamped_transcription
import stable_whisper
from datetime import datetime


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.api.crud import project_crud

from app.db.database import get_db
# from app.db.models import Project, ProjectCollaborator, User
# from app.api.models.projects import ProjectCreate, ProjectUpdate, CollaboratorEmailList, ProjectResponse, UserResponse
from app.utils.security import get_current_user
from app.utils.audio import extract_audio_segment, generate_speaker_srt
# from app.utils.email import send_invitation_email

from app.api.models.schemas import TranscriptionResponse, UserResponse, SummarizationResponse, TranscriptionRequest, SummarizationResponse, CaptionEnhancementRequest, EnhancedCaptionResponse, QnARequest, QnAResponse, CaptionGenerationResponse, SentimentAnalysisResponse, TranslationRequest, TranslationResponseB, TranscriptionEditResponse
from app.db.models import Transcription, File, Subtitle
# from app import models, schemas
import shutil
import os
from dotenv import load_dotenv
import google.generativeai as genai


from openai import OpenAI
from pyannote.audio import Pipeline
from pydub import AudioSegment
import torchaudio


load_dotenv()

# Initialize clients and models lazily
def get_openai_client():
    if not hasattr(get_openai_client, 'client'):
        get_openai_client.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return get_openai_client.client

def get_gemini_model():
    if not hasattr(get_gemini_model, 'model'):
        genai.configure(api_key=os.environ["GEMNI_API_KEY"])
        get_gemini_model.model = genai.GenerativeModel("gemini-1.5-flash")
    return get_gemini_model.model

def get_diarization_pipeline():
    if not hasattr(get_diarization_pipeline, 'pipeline'):
        try:
            HF_TOKEN = os.environ["HF_TOKEN"]
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN environment variable not set")
            get_diarization_pipeline.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=True
            )
        except Exception as e:
            print(f"Error initializing pipeline: {str(e)}")
            get_diarization_pipeline.pipeline = None
    return get_diarization_pipeline.pipeline

logger = logging.getLogger(__name__)  # Define or import logger

# router = APIRouter(
#     prefix="/transcriptions",
#     tags=["Transcriptions"],
# )


# @router.post("/", response_model=TranscriptionResponse)
# def create_transcription(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: UserResponse = Depends(get_current_user)
# ):

#     # Ensure the files directory exists
#     os.makedirs("files", exist_ok=True)

#     # Save uploaded file to disk
#     file_location = f"files/{file.filename}"
#     with open(file_location, "wb+") as file_object:
#         shutil.copyfileobj(file.file, file_object)

#     # Load Whisper model and transcribe the video
#     model = whisper.load_model("base")
#     transcription_result = model.transcribe(file_location)

#     # Use Stable-TS to get timestamped transcription
#     transcription_text = transcription_result['text']
#     print("transcription_text", transcription_text)
#     # timestamped_result = timestamped_transcription(file_location)

#     # Save transcription to the database
#     transcription = Transcription(
#         user_id=current_user.id,
#         original_filename=file.filename,
#         transcription_text=transcription_text
#     )
#     db.add(transcription)
#     db.commit()
#     db.refresh(transcription)

#     return transcription

# @router.get("/{id}", response_model=TranscriptionResponse)
# def get_transcription(id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     transcription = db.query(Transcription).filter(Transcription.id == id, Transcription.user_id == current_user.id).first()
#     if not transcription:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
#     return transcription

# @router.get("/", response_model=list[TranscriptionResponse])
# def list_transcriptions(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     transcriptions = db.query(Transcription).filter(Transcription.user_id == current_user.id).all()
#     return transcriptions

# @router.delete("/{id}")
# def delete_transcription(id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
#     transcription = db.query(Transcription).filter(Transcription.id == id, Transcription.user_id == current_user.id).first()
#     if not transcription:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
#     db.delete(transcription)
#     db.commit()
#     return {"message": "Transcription deleted"}


router = APIRouter(
    prefix="/projects/{project_id}/files/{file_id}/transcriptions",
    tags=["Transcriptions"],
)







def generate_srt(subtitles: List[dict]) -> str:
    srt_content = ""
    for index, subtitle in enumerate(subtitles):
        start_time = subtitle['start']
        end_time = subtitle['end']
        text = subtitle['text']

        start_time_str = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time % 1) * 1000):03}"
        end_time_str = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02},{int((end_time % 1) * 1000):03}"

        srt_content += f"{index + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n"

    return srt_content



def resample_audio(file_location, target_sample_rate=16000):
    waveform, sample_rate = torchaudio.load(file_location)
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
    return waveform




# Language prompt templates for different languages
# LANGUAGE_PROMPTS = {
#     'en': "Summarize this transcription and include action items, outlines,takeaways and suggestions:",
#     'es': "Resume esta transcripción e incluye elementos de acción, esquemas, conclusiones y sugerencias:",
#     'zh': "总结这段转录内容，包括行动项目、大纲、要点和建议：",
#     'fr': "Résumez cette transcription et incluez les points d'action, les grandes lignes, les points à retenir et les suggestions :",
#     'de': "Fassen Sie diese Transkription zusammen und fügen Sie Aktionspunkte, Gliederungen, Erkenntnisse und Vorschläge hinzu:",
#     'it': "Riassumi questa trascrizione e includi elementi di azione, schemi, spunti e suggerimenti:",
#     'ja': "この文字起こしを要約し、アクションアイテム、アウトライン、重要ポイント、提案を含めてください：",
#     'ko': "이 녹취록을 요약하고 실행 항목, 개요, 핵심 내용 및 제안을 포함하십시오:",
#     'pt': "Resuma esta transcrição e inclua itens de ação, esquemas, conclusões e sugestões:",
#     'ru': "Обобщите эту расшифровку и включите пункты действий, схемы, выводы и предложения:"
# }
LANGUAGE_PROMPTS = {
    'en': (
        "Summarize this transcription, including action items, outlines, emotional tone, key takeaways, and suggestions. "
        "Identify named entities such as people, places, dates, organizations, and other relevant information. "
        "Detect actionable tasks or commitments made during the conversation. "
        "Identify questions and their corresponding answers, and highlight important timestamps for quick navigation."
    ),
    'es': (
        "Resume esta transcripción e incluye elementos de acción, esquemas, tono emocional, conclusiones clave y sugerencias. "
        "Identifica entidades nombradas como personas, lugares, fechas, organizaciones y otra información relevante. "
        "Detecta tareas accionables o compromisos hechos durante la conversación. "
        "Identifica preguntas y sus respuestas correspondientes, y resalta marcas de tiempo importantes para una navegación rápida."
    ),
    'zh': (
        "总结这段转录内容，包括行动项目、大纲、情感基调、关键要点和建议。"
        "提取并识别人员、地点、日期、组织和其他相关信息。"
        "检测对话中的可执行任务或承诺。"
        "识别问题及其对应的答案，并突出显示重要的时间戳以便快速导航。"
    ),
    'fr': (
        "Résumez cette transcription en incluant les points d'action, les grandes lignes, le ton émotionnel, les points clés et les suggestions. "
        "Identifiez les entités nommées comme les personnes, lieux, dates, organisations et autres informations pertinentes. "
        "Détectez les tâches actionnables ou les engagements pris lors de la conversation. "
        "Identifiez les questions et leurs réponses correspondantes, et mettez en avant les moments clés pour une navigation rapide."
    ),
    'de': (
        "Fassen Sie diese Transkription zusammen und fügen Sie Aktionspunkte, Gliederungen, emotionale Tonalität, Schlüsselerkenntnisse und Vorschläge hinzu. "
        "Extrahieren und identifizieren Sie benannte Entitäten wie Personen, Orte, Daten, Organisationen und andere relevante Informationen. "
        "Erkennen Sie während des Gesprächs gemachte Aufgaben oder Verpflichtungen. "
        "Identifizieren Sie Fragen und die entsprechenden Antworten und heben Sie wichtige Zeitstempel hervor, um eine schnelle Navigation zu ermöglichen."
    ),
    'it': (
        "Riassumi questa trascrizione, includendo elementi di azione, schemi, tono emotivo, spunti chiave e suggerimenti. "
        "Identifica entità nominate come persone, luoghi, date, organizzazioni e altre informazioni rilevanti. "
        "Rileva compiti o impegni azionabili fatti durante la conversazione. "
        "Identifica domande e le relative risposte, e evidenzia i timestamp importanti per una navigazione rapida."
    ),
    'ja': (
        "この文字起こしを要約し、アクションアイテム、アウトライン、感情的なトーン、重要なポイント、提案を含めてください。"
        "人物、場所、日付、組織などの名前付きエンティティを抽出して特定します。"
        "会話中に行われた実行可能なタスクやコミットメントを検出します。"
        "質問とそれに対応する回答を特定し、迅速なナビゲーションのために重要なタイムスタンプを強調表示します。"
    ),
    'ko': (
        "이 녹취록을 요약하고 실행 항목, 개요, 감정적 톤, 핵심 내용 및 제안을 포함하십시오. "
        "사람, 장소, 날짜, 조직 및 기타 관련 정보를 추출하고 식별하십시오. "
        "대화 중에 수행 가능한 작업이나 약속을 감지하십시오. "
        "질문과 해당 답변을 식별하고 빠른 탐색을 위해 중요한 타임스탬프를 강조하십시오."
    ),
    'pt': (
        "Resuma esta transcrição e inclua itens de ação, esquemas, tom emocional, principais conclusões e sugestões. "
        "Identifique entidades nomeadas como pessoas, lugares, datas, organizações e outras informações relevantes. "
        "Detecte tarefas acionáveis ou compromissos feitos durante a conversa. "
        "Identifique perguntas e suas respectivas respostas, destacando os horários importantes para uma navegação rápida."
    ),
    'ru': (
        "Обобщите эту расшифровку и включите пункты действий, схемы, эмоциональный тон, ключевые выводы и предложения. "
        "Выделите именованные сущности, такие как люди, места, даты, организации и другую релевантную информацию. "
        "Обнаружьте задачи или обязательства, взятые во время разговора. "
        "Идентифицируйте вопросы и их соответствующие ответы, а также выделите важные временные метки для быстрой навигации."
    )
}


def get_summary_prompt(language: str, transcription_text: str) -> str:
    """
    Generate a language-appropriate prompt for the summary.
    
    Args:
        language: The detected language code (e.g., 'en', 'es', 'zh')
        transcription_text: The text to be summarized
        
    Returns:
        str: The complete prompt in the appropriate language
    """
    # Default to English if language is not supported
    base_prompt = LANGUAGE_PROMPTS.get(language.lower(), LANGUAGE_PROMPTS['en'])
    return f"{base_prompt} {transcription_text}"

@router.post("/", response_model=TranscriptionResponse)
def create_transcription(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    print("file retrieving")

    # Retrieve the file from the database
    file = db.query(File).filter(File.id == file_id, File.project_id == project_id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    print("file retrieved", file.path)
    # Download the file from Cloudinary
    response = requests.get(file.path)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download file from Cloudinary")

    # Save downloaded file to disk
    os.makedirs("files", exist_ok=True)
    file_location = f"files/{file_id}.wav"
    with open(file_location, "wb") as file_object:
        file_object.write(response.content)

    # Load Whisper model and transcribe the file
    model = whisper.load_model("base")
    transcription_result = model.transcribe(file_location)

    # diarization = pipeline(file_location)

    # if pipeline is None:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Speaker diarization pipeline not properly initialized"
    #         )

    # Load Whisper model
    # model = whisper.load_model("base")
    
    # # Perform diarization
    # diarization = pipeline(file_location)
    
    # # Initialize list for storing speaker segments
    # speaker_segments = []
    
    # # Process each speaker turn
    # for turn, _, speaker in diarization.itertracks(yield_label=True):
    #     segment_start = turn.start
    #     segment_end = turn.end
        
    #     # Extract audio segment for this speaker turn
    #     segment_path = extract_audio_segment(file_location, segment_start, segment_end)
        
    #     # Transcribe the segment
    #     segment_result = model.transcribe(segment_path)
        
    #     # Add to speaker segments with timing information
    #     speaker_segments.append({
    #         'speaker': speaker,
    #         'start': segment_start,
    #         'end': segment_end,
    #         'text': segment_result['text'].strip()
    #     })
        
    #     # Clean up temporary segment file
    #     os.remove(segment_path)

    # Generate SRT content with speaker labels
    # srt_content = generate_speaker_srt(speaker_segments)
    
    # # Generate plain transcription text with speaker labels
    # transcription_text = '\n'.join([
    #     f"[{segment['speaker']}]: {segment['text']}"
    #     for segment in speaker_segments
    # ])
    # print("speaker transcription" , transcription_text)
    # # Initialize an empty list for storing the final transcription with speakers
    # speaker_transcription = []
    # # Segment the audio by speaker and transcribe each segment
    # for turn, _, speaker in diarization.itertracks(yield_label=True):
    #     segment_start = turn.start
    #     segment_end = turn.end
    #     segment_audio = extract_audio_segment(file_location, segment_start, segment_end)  # Implement this to extract audio segments

    #     # Transcribe the segment
    #     segment_transcription = model.transcribe(segment_audio)
    #     speaker_transcription.append(f"Speaker {speaker}: {segment_transcription['text']}")

    # final_transcription = "\n".join(speaker_transcription)
    # print("final transcription", final_transcription)




    # Extract transcription text
    transcription_text = transcription_result['text']

    


    # print("transcription_result", transcription_result)
    # print("transcription_text", transcription_text)

    transcription_language = transcription_result.get('language', 'unknown')
    word_count = len(transcription_text.strip().split())
    # Calculate transcription duration
    if 'segments' in transcription_result and transcription_result['segments']:
        transcription_duration = transcription_result['segments'][-1]['end']
    else:
        transcription_duration = 0
    timestamp = datetime.utcnow()


    if transcription_text:
        # response = gemni_model.generate_content("summarize this transcription: " + transcription_text + "include some action items, outlines,  takeaways and suggestions")
        prompt = get_summary_prompt(transcription_language, transcription_text)
        response = get_gemini_model().generate_content(prompt)
        summary_text = response.text
    else:
        summary_text = ''
    # print("timestamp", timestamp)
    # print("word_count", word_count)
    # print("transcription_duration", transcription_duration)
    # print("language", transcription_language)

    # print("transcription_text", transcription_text)

    # srt generation
    # Ensure the transcription_result contains segments with timestamps
    if 'segments' not in transcription_result:
        logger.error("Transcription result does not contain segments with timestamps.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get timestamps from transcription.")

    # Generate SRT content
    subtitles = [{
        'start': segment['start'],
        'end': segment['end'],
        'text': segment['text']
    } for segment in transcription_result['segments']]

    srt_content = generate_srt(subtitles)

    # Save transcription SRT file
    srt_file_location = f"files/{file_id}.srt"
    with open(srt_file_location, "w") as srt_file:
        srt_file.write(srt_content)

    # Save transcription to the database
    transcription = Transcription(
        # user_id=current_user.id,
        project_id=project_id,
        file_id=file_id,
        # original_filename=file.name,
        transcription_text=srt_content,
        summary_text=summary_text,
        repurposed_text='',
        language=transcription_language,
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

     # Create subtitle entry
    try:
        # Generate SRT format subtitles
        segments = transcription_result.get('segments', [])
        srt_content = generate_srt([{
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text']
        } for segment in segments])

        # Create subtitle entry
        db_subtitle = Subtitle(
            transcription_id= transcription.id,
            subtitle_format='srt',
            subtitle_text=srt_content
        )
        db.add(db_subtitle)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to create subtitle: {str(e)}")
        # Don't raise exception here as transcription was successful
        
    # Clean up the temporary file
    try:
        os.remove(file_location)
    except Exception as e:
        logger.error(f"Failed to remove temporary file: {str(e)}")



    return transcription

# @router.post("/", response_model=TranscriptionResponse)
# def create_transcription(
#         project_id: int,
#         file_id: int,
#         db: Session = Depends(get_db),
#         current_user: UserResponse = Depends(get_current_user)
# ):
#     print("Retrieving file from database")

#     # Step 1: Retrieve the file from the database
#     file = db.query(File).filter(File.id == file_id, File.project_id == project_id).first()
#     if not file:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

#     print("File retrieved:", file.path)

#     # Step 2: Download the file from Cloudinary (or a similar file storage)
#     response = requests.get(file.path)
#     if response.status_code != 200:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download file")

#     # Step 3: Save the downloaded file locally
#     os.makedirs("files", exist_ok=True)
#     file_location = f"files/{file_id}.wav"
#     with open(file_location, "wb") as file_object:
#         file_object.write(response.content)


#     # Resample the audio file to ensure consistent sample rate
#     waveform = resample_audio(file_location)

#     # Step 4: Perform speaker diarization using PyAnnote
#     diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=os.environ.get("HF_TOKEN"))
#     diarization_result = diarization_pipeline(file_location)

#     # Step 5: Load Whisper model for transcription
#     model = whisper.load_model("base")

#     # Step 6: Process each diarized segment and perform transcription
#     audio = AudioSegment.from_wav(file_location)
#     transcription_text = ""
#     speaker_transcriptions = []

#     for segment in diarization_result.itertracks(yield_label=True):
#         start_time = segment[0].start
#         end_time = segment[0].end
#         speaker = segment[2]  # Speaker label

#         # Step 7: Extract audio segment for the current speaker
#         audio_segment = audio[start_time * 1000: end_time * 1000]  # Convert time to milliseconds
#         segment_file_location = f"files/{file_id}_segment_{start_time}-{end_time}.wav"
#         audio_segment.export(segment_file_location, format="wav")

#         # Step 8: Transcribe the audio segment using Whisper
#         segment_transcription = model.transcribe(segment_file_location)['text']
#         transcription_text += f"Speaker {speaker}: {segment_transcription}\n"

#         # Step 9: Store transcription details for SRT generation
#         speaker_transcriptions.append({
#             'speaker': speaker,
#             'start': start_time,
#             'end': end_time,
#             'text': segment_transcription
#         })

#     # Step 10: Generate SRT content and save the transcription details
#     transcription_language = 'unknown'  # Optionally, add more logic to detect language
#     word_count = len(transcription_text.strip().split())
#     timestamp = datetime.utcnow()

#     print("Transcription completed:", transcription_text)

#     # Step 11: Save SRT file
#     srt_file_location = f"files/{file_id}.srt"
#     srt_content = generate_srt(speaker_transcriptions)
#     with open(srt_file_location, "w") as srt_file:
#         srt_file.write(srt_content)

#     print("srt_content = ", srt_content)

#     # Step 12: Save transcription details to the database
#     transcription = Transcription(
#         project_id=project_id,
#         file_id=file_id,
#         transcription_text=srt_content,
#         language=transcription_language,
#         # word_count=word_count,
#         created_at=timestamp,
#         updated_at=timestamp
#     )
#     db.add(transcription)
#     db.commit()
#     db.refresh(transcription)

#     # Step 13: Return the response with transcription details
#     return transcription


@router.put("/{id}")
def update_transcription(
    project_id: int,
    file_id: int,
    id: int,
    transcription_data: TranscriptionEditResponse,
    db: Session = Depends(get_db)
):
    transcription = db.query(Transcription).filter(
        Transcription.project_id == project_id,
        Transcription.file_id == file_id,
        Transcription.id == id
    ).first()

    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    transcription.transcription_text = transcription_data.transcription_text
    db.commit()
    db.refresh(transcription)
    
    return {"message": "Transcription updated successfully", "transcription": transcription}
@router.get("/{id}", response_model=TranscriptionResponse)
def get_transcription(id: int, db: Session = Depends(get_db),
current_user: UserResponse = Depends(get_current_user)):
    transcription = db.query(Transcription).filter(Transcription.id == id).first()
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
    return transcription



@router.get("/", response_model=list[TranscriptionResponse])
def list_transcriptions(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db),
current_user: UserResponse = Depends(get_current_user)):
    db_project = project_crud.get_project(db, project_id=project_id)
    transcriptions = db.query(Transcription).filter(db_project.user_id == current_user.id).all()
    return transcriptions

@router.delete("/{id}")
def delete_transcription(
     project_id: int,
    file_id: int,
    id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):

    db_project = project_crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    transcription = db.query(Transcription).filter(Transcription.id == id).first()
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
    db.delete(transcription)
    db.commit()
    return {"message": "Transcription deleted"}



# ChatGPT Summarization
@router.post("/{id}/summarize-transcription", response_model=SummarizationResponse)
async def summarize_transcription(
     project_id: int,
     file_id: int,
     id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    db_project = project_crud.get_project(db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    transcription = db.query(Transcription).filter(Transcription.id == id).first()
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

    try:
        # OpenAI Summarization using the new interface
        response = get_openai_client().chat.completions.create(
            model="gpt-3.5-turbo",  # Change this to the appropriate model you're using
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following transcription:\n{transcription.transcription_text}"}
            ],
            max_tokens=150
        )
        # summary = response['choices'][0]['message']['content'].strip()
        summary = response.choices[0].message.content.strip()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Caption Enhancement
@router.post("/{id}/enhance-captions", response_model=EnhancedCaptionResponse)
async def enhance_captions(
     project_id: int,
     file_id: int,
    db: Session = Depends(get_db),
    request: CaptionEnhancementRequest = Depends(get_current_user)
):
    try:
        # OpenAI Caption Enhancement
        response = get_openai_client().Completion.create(
            engine="text-davinci-003",
            prompt=f"Enhance the following captions:\n{request.subtitle_text}",
            max_tokens=150
        )
        enhanced_subtitles = response.choices[0].text.strip()
        return {"enhanced_subtitles": enhanced_subtitles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # Q&A on Transcription
# @router.post("/{id}/ask-chatgpt", response_model=QnAResponse)
# async def ask_chatgpt(
#     project_id: int = Path(...),
#     request: QnARequest = Body(...)
# ):
#     try:
#         # OpenAI Q&A
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=f"Based on the following transcription, answer this question:\nTranscription: {request.transcription_text}\nQuestion: {request.question}",
#             max_tokens=150
#         )
#         answer = response.choices[0].text.strip()
#         return {"answer": answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Stylized Caption Generation
# @router.post("/{id}/generate-stylized-captions", response_model=CaptionGenerationResponse)
# async def generate_stylized_captions(
#     project_id: int = Path(...),
#     request: CaptionGenerationRequest = Body(...)
# ):
#     try:
#         # OpenAI Caption Generation
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=f"Generate {request.style} captions based on this transcription:\n{request.transcription_text}",
#             max_tokens=150
#         )
#         captions = response.choices[0].text.strip()
#         return {"captions": captions}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Sentiment Analysis
# @router.post("/{id}/analyze-sentiment", response_model=SentimentAnalysisResponse)
# async def analyze_sentiment(
#     project_id: int = Path(...),
#     request: TranscriptionRequest = Body(...)
# ):
#     try:
#         # OpenAI Sentiment Analysis
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=f"Analyze the sentiment of the following transcription:\n{request.transcription_text}",
#             max_tokens=100
#         )
#         sentiment = response.choices[0].text.strip()
#         insights = "Based on the transcription, the general sentiment appears to be " + sentiment
#         return {"sentiment": sentiment, "insights": insights}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Translation Assistance
# @router.post("/{id}/translate-transcription", response_model=TranslationResponseB)
# async def translate_transcription(
#     project_id: int = Path(...),
#     request: TranslationRequest = Body(...)
# ):
#     try:
#         # OpenAI Translation
#         response = openai.Completion.create(
#             engine="text-davinci-003",
#             prompt=f"Translate this transcription to {request.target_language}:\n{request.transcription_text}",
#             max_tokens=150
#         )
#         translated_text = response.choices[0].text.strip()
#         return {"translated_text": translated_text}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
