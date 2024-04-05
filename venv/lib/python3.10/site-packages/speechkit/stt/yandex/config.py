from dataclasses import dataclass
from typing import Optional

from ..recognizer import RecognitionConfig, AudioProcessingType


@dataclass
class YandexRecognitionConfig(RecognitionConfig):
    model: Optional[str] = None
    language: Optional[str] = None
    audio_processing_type: AudioProcessingType = AudioProcessingType.Full
    data_logging: bool = False
