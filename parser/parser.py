import requests
import time
from typing import Optional
from utils.logger import setupLogger

logger = setupLogger('parser', 'parser.log')


def getAnswer(egeNo: int, topicNo: int, max_retries: int = 3) -> str:
    url = f'https://kpolyakov.spb.ru/school/ege/getanswer.php?egeNo={egeNo}&topicNo={topicNo}'

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if response.text.find('<br/><a href') == -1:
                return response.text

            if response.text[:response.text.find('<br/><a href')]:
                return response.text[:response.text.find('<br/><a href')].replace('<br/>', ' ')
            else:
                return response.content.decode('utf-8', errors='ignore').replace('<br/>', ' ')

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1} for egeNo={egeNo}, topicNo={topicNo}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"Ошибка: превышено время ожидания запроса"

        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt + 1} for egeNo={egeNo}, topicNo={topicNo}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"Ошибка: не удалось подключиться к серверу"

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for egeNo={egeNo}, topicNo={topicNo}: {e}")
            return f"Ошибка выполнения запроса: HTTP {e.response.status_code}"

        except Exception as e:
            logger.error(f"Unexpected error for egeNo={egeNo}, topicNo={topicNo}: {e}")
            return f"Ошибка выполнения запроса: {str(e)}"

    return "Ошибка: не удалось получить ответ после нескольких попыток"
