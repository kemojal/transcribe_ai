from moviepy.editor import TextClip

from app.api.models.schemas import Entry, TextStyle


# Helper function to convert timestamp format (e.g., '00:00:03,000') to seconds
# def parse_timestamp(timestamp: str) -> float:
#     h, m, s = timestamp.split(":")
#     s, ms = s.split(",")
#     return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

# Function to create text clips based on the input data
def create_text_clip(entry: Entry, style: TextStyle, video_size):
    # Create the TextClip
    text_clip = TextClip(
        entry.content,
        font=style.font_family,
        fontsize=style.font_size,
        color=style.color
    ).set_position(('center', 'bottom')).set_duration(entry.timestamp_end - entry.timestamp_start)

    return text_clip