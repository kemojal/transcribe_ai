from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import metrics

# Audio Processing Metrics
audio_file_size_bytes = Histogram(
    "audio_file_size_bytes",
    "Size of audio files being processed",
    ["format"],
    buckets=[1000000, 5000000, 10000000, 25000000, 50000000, 100000000]  # 1MB to 100MB
)

audio_processing_duration_seconds = Histogram(
    "audio_processing_duration_seconds",
    "Time taken to process audio files",
    ["format"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]  # 0.1s to 1min
)

audio_format_errors_total = Counter(
    "audio_format_errors_total",
    "Total number of audio format errors",
    ["error_type"]
)

# Transcription Metrics
transcription_requests_total = Counter(
    "transcription_requests_total",
    "Total number of transcription requests",
    ["model"]
)

transcription_duration_seconds = Histogram(
    "transcription_duration_seconds",
    "Time taken to transcribe audio",
    ["model"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]  # 1s to 10min
)

transcription_failures_total = Counter(
    "transcription_failures_total",
    "Total number of transcription failures",
    ["error_type"]
)

transcription_confidence_score = Gauge(
    "transcription_confidence_score",
    "Confidence score of transcriptions",
    ["model"]
)

transcription_queue_size = Gauge(
    "transcription_queue_size",
    "Current size of the transcription queue"
)

# Custom metrics instrumentator
def custom_metrics():
    return [
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="transcribe_ai",
            metric_subsystem="http",
        ),
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="transcribe_ai",
            metric_subsystem="http",
        ),
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="transcribe_ai",
            metric_subsystem="http",
        ),
    ] 