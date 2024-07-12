import requests


def getAnswer(egeNo:int, topicNo:int) -> str:

    request = f'https://kpolyakov.spb.ru/school/ege/getanswer.php?egeNo={egeNo}&topicNo={topicNo}'
    response = requests.get(request)

    if response:
        if response.text.find('<br/><a href') == -1:
            return response.text
        if response.text[:response.text.find('<br/><a href')]:
            return response.text[:response.text.find('<br/><a href')].replace('<br/>', '\n')
        else:
           return response.content.replace('<br/>', '\n')
    else:
        result = "Ошибка выполнения запроса:" + str(request)
        result += f"\nHttp статус: {response.status_code} ({response.reason})"
        return result


print(getAnswer(15, 147))
