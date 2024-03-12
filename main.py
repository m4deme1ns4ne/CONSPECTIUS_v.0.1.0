from get_giga_token import get_giga_token
from requests_for_text_generation import get_chat_completion
from logger import file_logger

from loguru import logger


@logger.catch
def main():
    file_logger()
    giga_token = get_giga_token()
    text = input("Введите текст запроса: ")
    try:
        answer = get_chat_completion(giga_token, text)
    except:
        logger.error('Ошибка при получении ответа')
    print(answer.json()['choices'][0]['message']['content'])
    logger.info("Ответ получен и выведен")


if __name__ == "__main__":
    main()