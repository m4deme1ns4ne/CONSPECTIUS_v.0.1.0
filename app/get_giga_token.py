from get_token import get_token
from loguru import logger
from auth import auth


@logger.catch
def get_giga_token():
    try:
        response = get_token(auth)
        logger.info("Токен получен")
        return response.json()['access_token']
    except Exception as err:
        logger.error(err)