from .creds import YandexCredentials


class Environment:
    @property
    def yandex_credentials(self) -> YandexCredentials:
        return self._yandex_creds

    @yandex_credentials.setter
    def yandex_credentials(self, creds: YandexCredentials):
        self._yandex_creds = creds

    def __init__(self):
        self._yandex_creds = None


__ENV: Environment = None


def environment() -> Environment:
    global __ENV
    if __ENV is None:
        __ENV = Environment()
    return __ENV


def get_yandex_credentials() -> YandexCredentials:
    return environment().yandex_credentials


def configure_credentials(
    yandex_credentials: YandexCredentials = None
):
    if yandex_credentials is not None:
        environment().yandex_credentials = yandex_credentials
