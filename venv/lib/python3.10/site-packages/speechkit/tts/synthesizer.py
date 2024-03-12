from abc import ABC, abstractmethod
from typing import Union, Optional
from dataclasses import dataclass

import pydub
from enum import Enum


class AudioEncoding(Enum):
    PCM = 1
    WAV = 2
    OGG_OPUS = 3
    MP3 = 4


class TextFormat(Enum):
    TEXT = 1
    SSML = 2


@dataclass
class SynthesisConfig:
    audio_encoding: AudioEncoding = AudioEncoding.WAV
    voice: Optional[str] = None


class SynthesisModel(ABC):
    def __init__(self, config: Optional[SynthesisConfig] = None):
        if config is None:
            config = SynthesisConfig()
        self._config = config

    @abstractmethod
    def synthesize(
        self,
        text: str,
        synthesis_config: Optional[SynthesisConfig] = None,
        *,
        raw_format: bool = False
    ) -> Union[bytes, pydub.AudioSegment]:
        """
        Service-dependent implementation of speech synthesis
        :param text: text to synthesize
        :param synthesis_config: custom synthesis config to override default model config
        :param raw_format: return bytes instead of pydub.AudioSegment representation
        :return: synthesized audio
        """
        pass

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
    def audio_encoding(self) -> AudioEncoding:
        """
        Get output format
        """
        return self._get_config_parameter('audio_encoding')

    @audio_encoding.setter
    def audio_encoding(self, value: AudioEncoding):
        """
        Set output format
        """
        self._set_config_parameter('audio_encoding', value)

    @property
    def sample_rate(self) -> int:
        """
        Get output sample rate (if available)
        """
        return self._get_config_parameter('sample_rate')

    @sample_rate.setter
    def sample_rate(self, value: int):
        """
        Set output sample rate (if available)
        """
        self._set_config_parameter('sample_rate', value)

    @property
    def voice(self) -> str:
        """
        Get speaker name
        """
        return self._get_config_parameter('voice')

    @voice.setter
    def voice(self, value: str):
        """
        Set speaker name
        """
        self._set_config_parameter('voice', value)

    @property
    def text_format(self) -> TextFormat:
        """
        Get text format (if available)
        """
        return self._get_config_parameter('text_format')

    @text_format.setter
    def text_format(self, value: TextFormat):
        """
        Set text format (if available)
        """
        self._set_config_parameter('text_format', value)

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
