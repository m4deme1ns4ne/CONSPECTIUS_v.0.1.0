from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..synthesizer import SynthesisConfig, AudioEncoding


@dataclass
class TextTemplateVar:
    name: str
    value: str


@dataclass
class TextTemplate:
    text: str
    variables: List[TextTemplateVar]


@dataclass
class AudioTemplateVar:
    name: str
    start_ms: int
    length_ms: int


@dataclass
class AudioTemplate:
    audio: bytes
    variables: List[AudioTemplateVar]
    audio_format: AudioEncoding
    sample_rate: int = None


class LoudnessNormalizationType(Enum):
    MAX_PEAK = 1
    LUFS = 2


@dataclass
class YandexSynthesisConfig(SynthesisConfig):
    model: Optional[str] = None
    sample_rate: int = 22050
    role: Optional[str] = None
    speed: Optional[float] = None
    volume: Optional[float] = None
    norm_type: LoudnessNormalizationType = LoudnessNormalizationType.LUFS
    unsafe_mode: bool = True  # enables long texts synthesis
    data_logging: bool = False
