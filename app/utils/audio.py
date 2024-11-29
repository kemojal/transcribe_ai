from pydub import AudioSegment

# Define the extract_audio_segment function
def extract_audio_segment(file_path, start_time, end_time):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Extract the segment
    start_ms = start_time * 1000  # Convert to milliseconds
    end_ms = end_time * 1000      # Convert to milliseconds
    segment = audio[start_ms:end_ms]

    # Create a temporary file for the segment
    segment_file_path = f"files/segment_{start_time}_{end_time}.wav"
    segment.export(segment_file_path, format="wav")

    return segment_file_path



def generate_speaker_srt(speaker_segments):
    """Generate SRT content with speaker labels."""
    srt_content = []
    for i, segment in enumerate(speaker_segments, 1):
        # Format timestamps
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        
        # Format SRT entry
        srt_entry = (
            f"{i}\n"
            f"{start_time} --> {end_time}\n"
            f"[{segment['speaker']}] {segment['text']}\n\n"
        )
        srt_content.append(srt_entry)
    
    return ''.join(srt_content)

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"