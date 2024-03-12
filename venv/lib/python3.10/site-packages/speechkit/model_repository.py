from typing import Optional, Tuple, List, Union, Type

from speechkit.stt import RecognitionModel
from speechkit.stt.yandex import YandexRecognizer

from speechkit.tts import SynthesisModel
from speechkit.tts.yandex import YandexSynthesizer


def _create_model(
    custom_endpoint: Tuple[str, bool],
    custom_headers: List[Tuple[str, str]],
    constructor: Union[Type[YandexRecognizer], Type[YandexSynthesizer]]
):
    if custom_endpoint is not None:
        endpoint, ssl = custom_endpoint
        model = constructor(endpoint=endpoint, use_ssl=ssl, custom_headers=custom_headers)
    else:
        model = constructor(custom_headers=custom_headers)

    return model


def synthesis_model(
    custom_endpoint: Tuple[str, bool] = None,
    custom_headers: List[Tuple[str, str]] = None
) -> SynthesisModel:
    return _create_model(custom_endpoint, custom_headers, YandexSynthesizer)


def recognition_model(
    custom_endpoint: Optional[Tuple[str, bool]] = None,
    custom_headers: List[Tuple[str, str]] = None
) -> RecognitionModel:
    return _create_model(custom_endpoint, custom_headers, YandexRecognizer)
