from typing import Optional


class YandexCredentials:
    def __init__(self, *, api_key: Optional[str] = None, iam_token: Optional[str] = None):
        assert sum((api_key is None, iam_token is None)), 'only one of api_key or iam_token should be provided'
        self._api_key = api_key
        self._iam_token = iam_token

    @property
    def api_key(self):
        return self._api_key

    @property
    def iam_token(self):
        return self._iam_token
