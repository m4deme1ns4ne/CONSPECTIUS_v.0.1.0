import io
from abc import ABC, abstractmethod
from typing import List, Union, Optional
from dataclasses import dataclass
from pathlib import Path
from pydub import AudioSegment
from enum import Enum

from .transcription import Transcription


@dataclass
class RecognitionConfig:
    pass


class AudioProcessingType(Enum):
    Full = 'full'
    Stream = 'stream'


class RecognitionModel(ABC):
    def __init__(self, config: Optional[RecognitionConfig] = None):
        if config is None:
            config = RecognitionConfig()
        self._config = config

    @abstractmethod
    def _transcribe_impl(
        self,
        audio: AudioSegment,
        recognition_config: RecognitionConfig
    ) -> List[Transcription]:
        """
        Service-dependent implementation of speech recognition
        """
        pass

    def transcribe(
        self,
        audio: Union[bytes, AudioSegment],
        recognition_config: Optional[RecognitionConfig] = None
    ) -> List[Transcription]:
        """
        Transcribe audio
        :param audio: audio representation (bytes or pydub.AudioSegment)
        :param recognition_config: custom recognition config to override default model config
        :return: per-channel audio transcriptions
        """
        if isinstance(audio, bytes):
            audio = AudioSegment.from_file(io.BytesIO(audio))
        if recognition_config is None:
            recognition_config = self._config
        return self._transcribe_impl(audio, recognition_config)

    def transcribe_file(
        self,
        audio_path: Union[str, Path],
        recognition_config: Optional[RecognitionConfig] = None
    ) -> List[Transcription]:
        """
        Transcribe audio from file
        :param audio_path: path to audio file
        :param recognition_config: custom recognition config to override default model config
        :return: per-channel audio transcriptions
        """
        audio = AudioSegment.from_file(str(audio_path))
        return self.transcribe(audio, recognition_config)

    def _get_config_parameter(self, parameter_name):
        if hasattr(self._config, parameter_name):
            return getattr(self._config, parameter_name)
        print(f'Parameter `{parameter_name}` is not supported by the selected API')
        return None

    def _set_config_parameter(self, parameter_name, parameter_value):
        if hasattr(self._config, parameter_name):
            setattr(self._config, parameter_name, parameter_value)
            return
        print(f'Parameter `{parameter_name}` is not supported by the selected API')

    @property
    def model(self):
        """
        Get speech recognition model (service-dependent)
        """
        return self._get_config_parameter('model')

    @model.setter
    def model(self, value):
        """
        Get speech recognition model (service-dependent)
        """
        self._set_config_parameter('model', value)

    @property
    def language(self):
        """
        Get speech recognition language (if available)
        """
        return self._get_config_parameter('language')

    @language.setter
    def language(self, value):
        """
        Set speech recognition language (if available)
        """
        self._set_config_parameter('language', value)

    @property
    def audio_processing_type(self):
        """
        Get audio processing type (if available)
        """
        return self._get_config_parameter('audio_processing_type')

    @audio_processing_type.setter
    def audio_processing_type(self, value):
        """
        Set audio processing type (if available)
        """
        self._set_config_parameter('audio_processing_type', value)

    @property
    def data_logging(self) -> bool:
        """
        Get data_logging value (if available)
        """
        return self._get_config_parameter('data_logging')

    @data_logging.setter
    def data_logging(self, value: bool):
        """
        Get data_logging value (if available)
        """
        self._set_config_parameter('data_logging', value)
