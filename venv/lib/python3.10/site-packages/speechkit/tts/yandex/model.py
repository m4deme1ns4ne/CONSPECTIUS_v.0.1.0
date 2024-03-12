import io
import grpc
import uuid
import pydub
from typing import Union, Optional, Tuple, List

from yandex.cloud.ai.tts.v3 import tts_pb2, tts_service_pb2_grpc

from ...common.apis import YandexModel
from ...common.utils import get_yandex_credentials

from ..synthesizer import SynthesisModel, SynthesisConfig, AudioEncoding
from .config import YandexSynthesisConfig, LoudnessNormalizationType, AudioTemplate, TextTemplate


class YandexSynthesizer(SynthesisModel, YandexModel):
    def __init__(
        self,
        endpoint: str = 'tts.api.cloud.yandex.net:443',
        use_ssl: bool = True,
        custom_headers: List[Tuple[str, str]] = None,
        **kwargs
    ):
        SynthesisModel.__init__(self, YandexSynthesisConfig())
        YandexModel.__init__(self, endpoint, use_ssl, custom_headers)

        while True:
            try:
                grpc.channel_ready_future(self._channel).result(timeout=10)
                break
            except grpc.FutureTimeoutError:
                print("Synthesizer service is temporarily unavailable")

    @staticmethod
    def _audio_spec(audio_format: AudioEncoding, sample_rate: int):
        if audio_format == AudioEncoding.PCM:
            return tts_pb2.AudioFormatOptions(
                raw_audio=tts_pb2.RawAudio(
                    audio_encoding=tts_pb2.RawAudio.AudioEncoding.LINEAR16_PCM, sample_rate_hertz=sample_rate
                )
            )
        elif audio_format == AudioEncoding.WAV:
            return tts_pb2.AudioFormatOptions(
                container_audio=tts_pb2.ContainerAudio(
                    container_audio_type=tts_pb2.ContainerAudio.ContainerAudioType.WAV
                )
            )
        elif audio_format == AudioEncoding.OGG_OPUS:
            return tts_pb2.AudioFormatOptions(
                container_audio=tts_pb2.ContainerAudio(
                    container_audio_type=tts_pb2.ContainerAudio.ContainerAudioType.OGG_OPUS
                )
            )
        elif audio_format == AudioEncoding.MP3:
            return tts_pb2.AudioFormatOptions(
                container_audio=tts_pb2.ContainerAudio(
                    container_audio_type=tts_pb2.ContainerAudio.ContainerAudioType.MP3
                )
            )

    @staticmethod
    def _norm_type(norm_type: LoudnessNormalizationType):
        if norm_type == LoudnessNormalizationType.MAX_PEAK:
            return tts_pb2.UtteranceSynthesisRequest.LoudnessNormalizationType.MAX_PEAK
        elif norm_type == LoudnessNormalizationType.LUFS:
            return tts_pb2.UtteranceSynthesisRequest.LoudnessNormalizationType.LUFS

    @staticmethod
    def _gen_request(
        text: Union[str, TextTemplate],
        audio_template: Optional[AudioTemplate],
        synthesis_config: YandexSynthesisConfig
    ):
        request = tts_pb2.UtteranceSynthesisRequest(
            model=synthesis_config.model,
            output_audio_spec=YandexSynthesizer._audio_spec(synthesis_config.audio_encoding, synthesis_config.sample_rate),
            loudness_normalization_type=YandexSynthesizer._norm_type(synthesis_config.norm_type),
            unsafe_mode=synthesis_config.unsafe_mode,
        )

        if isinstance(text, str):
            request.text = text
        elif isinstance(text, TextTemplate):
            if audio_template is None:
                raise ValueError("provide audio template please")

            text_template = tts_pb2.TextTemplate()
            text_template.text_template = text.text
            for text_var in text.variables:
                var = text_template.variables.add()
                var.variable_name = text_var.name
                var.variable_value = text_var.value
            request.text_template.CopyFrom(text_template)

            hint = request.hints.add()
            hint.audio_template.CopyFrom(
                tts_pb2.AudioTemplate(
                    audio=tts_pb2.AudioContent(
                        content=audio_template.audio,
                        audio_spec=YandexSynthesizer._audio_spec(
                            audio_template.audio_format,
                            audio_template.sample_rate,
                        ),
                    ),
                    text_template=text_template,
                )
            )
            for audio_var in audio_template.variables:
                var = hint.audio_template.variables.add()
                var.variable_name = audio_var.name
                var.variable_start_ms = audio_var.start_ms
                var.variable_length_ms = audio_var.length_ms
        else:
            raise Exception(f"Class {type(text).__name__} is not supported input for synthesizer")

        if synthesis_config.voice is not None:
            hint = request.hints.add()
            hint.voice = synthesis_config.voice
        if synthesis_config.role is not None:
            hint = request.hints.add()
            hint.role = synthesis_config.role
        if synthesis_config.speed is not None:
            hint = request.hints.add()
            hint.speed = synthesis_config.speed
        if synthesis_config.volume is not None:
            hint = request.hints.add()
            hint.volume = synthesis_config.volume
        return request

    def _synthesize_impl(
        self,
        text: Union[str, TextTemplate],
        audio_template: Optional[AudioTemplate] = None,
        synthesis_config: Optional[SynthesisConfig] = None,
        raw_format: bool = False
    ) -> Union[bytes, pydub.AudioSegment]:
        if synthesis_config is None:
            synthesis_config = self._config

        if not isinstance(synthesis_config, YandexSynthesisConfig):
            synthesis_config = YandexSynthesisConfig(**synthesis_config.__dict__)

        if not raw_format:
            synthesis_config.audio_encoding = AudioEncoding.WAV

        req_id = str(uuid.uuid4())
        stub = tts_service_pb2_grpc.SynthesizerStub(self._channel)

        try:
            yandex_creds = get_yandex_credentials()
            if yandex_creds.api_key is not None:
                authorization_header = f'Api-Key {yandex_creds.api_key}'
            else:
                authorization_header = f'Bearer {yandex_creds.iam_token}'

            metadata = [
                ('authorization', authorization_header),
                ('x-client-request-id', req_id),
                *self._custom_headers
            ]

            if synthesis_config.data_logging:
                metadata.append(('x-data-logging-enabled', 'true'))

            it = stub.UtteranceSynthesis(
                self._gen_request(text, audio_template, synthesis_config),
                metadata=metadata
            )

            wave = io.BytesIO()
            for r in it:
                wave.write(r.audio_chunk.data)

            result = wave.getbuffer().tobytes()
            if not raw_format:
                result = pydub.AudioSegment(result)
            return result
        except grpc.RpcError as err:
            print(f'Failed to synthesize audio, request_id={req_id}. RPC Error: {err}')
            raise err
        except Exception as err:
            print(f'Failed to synthesize audio, request_id={req_id}. Error: {err}')
            raise err

    def synthesize(
        self,
        text: str,
        synthesis_config: Optional[SynthesisConfig] = None,
        *,
        raw_format: bool = False
    ) -> Union[bytes, pydub.AudioSegment]:
        return self._synthesize_impl(text, None, synthesis_config, raw_format)

    def synthesize_template(
        self,
        text: TextTemplate,
        audio_template: AudioTemplate,
        synthesis_config: Optional[SynthesisConfig] = None,
        *,
        raw_format: bool = False
    ) -> Union[bytes, pydub.AudioSegment]:
        return self._synthesize_impl(text, audio_template, synthesis_config, raw_format)

    @property
    def model(self) -> str:
        """
        Get model name
        """
        return self._get_config_parameter('model')

    @model.setter
    def model(self, value: str):
        """
        Set model name
        """
        self._set_config_parameter('model', value)

    @property
    def role(self) -> str:
        """
        Get speaker role
        """
        return self._get_config_parameter('role')

    @role.setter
    def role(self, value: str):
        """
        Set speaker role
        """
        self._set_config_parameter('role', value)

    @property
    def speed(self) -> float:
        """
        Get audio speed
        """
        return self._get_config_parameter('speed')

    @speed.setter
    def speed(self, value: float):
        """
        Set audio speed
        """
        self._set_config_parameter('speed', value)

    @property
    def volume(self) -> float:
        """
        Get volume
        """
        return self._get_config_parameter('volume')

    @volume.setter
    def volume(self, value: float):
        """
        Set volume
        """
        self._set_config_parameter('volume', value)

    @property
    def norm_type(self) -> LoudnessNormalizationType:
        """
        Get audio normalization type
        """
        return self._get_config_parameter('norm_type')

    @norm_type.setter
    def norm_type(self, value: LoudnessNormalizationType):
        """
        Set audio normalization type
        """
        self._set_config_parameter('norm_type', value)

    @property
    def unsafe_mode(self) -> bool:
        """
        Get unsafe_mode value
        """
        return self._get_config_parameter('unsafe_mode')

    @unsafe_mode.setter
    def unsafe_mode(self, value: bool):
        """
        Set unsafe_mode value
        """
        self._set_config_parameter('unsafe_mode', value)
