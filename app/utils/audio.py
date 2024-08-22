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