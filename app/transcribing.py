import assemblyai as aai
import time
from loguru import logger

from assemblyai_apikey import my_api_key


def transcribing_aai():
    logger.info("Начало транскрибации")
    start_time = time.perf_counter()

    # API key
    aai.settings.api_key = my_api_key

    transcriber = aai.Transcriber()
    audio_url = (
        "/Users/aleksandrvolzanin/my-python/транскрипипапупипипи/data/audio_2024-04-03_13-56-19.ogg"
    )
    config = aai.TranscriptionConfig(language_code="ru")
    transcript = transcriber.transcribe(audio_url, config)
    end_time = time.perf_counter()

    logger.info("Конец транскрибации")