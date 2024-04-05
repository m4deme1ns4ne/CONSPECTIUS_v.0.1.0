import requests
import uuid
from loguru import logger


@logger.catch
def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    """
      Выполняет POST-запрос к эндпоинту, который выдает токен.

      Параметры:
      - auth_token (str): токен авторизации, необходимый для запроса.
      - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

      Возвращает:
      - ответ API, где токен и срок его "годности".
      """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': rq_uid,
            'Authorization': f'Basic {auth_token}'
        }
        logger.info(f"Код аутентификации получен")
    except Exception as err:
        logger.error(err)

    # Тело запроса
    payload = {
        'scope': scope
    }

    # Делаем POST запрос с отключенной SSL верификацией
    # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        logger.info(f"Ответ получен")
    except Exception as err:
        logger.error(err)
    return response