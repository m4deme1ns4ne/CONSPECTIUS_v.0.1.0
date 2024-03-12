import grpc
from typing import Tuple, List


class YandexModel:
    def __init__(self, endpoint: str, use_ssl: bool, custom_headers: List[Tuple[str, str]]):
        self._custom_headers = custom_headers or []

        opts = [('grpc.max_message_length', 128 * 1024 * 1024)]
        if use_ssl:
            cred = grpc.ssl_channel_credentials()
            self._channel = grpc.secure_channel(endpoint, cred, options=opts)
        else:
            self._channel = grpc.insecure_channel(endpoint, options=opts)
