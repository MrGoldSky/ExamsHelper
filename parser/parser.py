import json, requests


def getAnswer(egeNo, topicNo):

    response = requests.get(f'https://kpolyakov.spb.ru/school/ege/getanswer.php?egeNo={egeNo}&topicNo={topicNo}')

    if response:
        if response.text[:response.text.find('<br/><a href')]:
            return response.text[:response.text.find('<br/><a href')].replace('<br/>', '\n')
        else:
           return response.content.replace('<br/>', '\n')
    else:
        result = "Ошибка выполнения запроса:" + str(request)
        result += f"\nHttp статус: {response.status_code} ({response.reason})"
        return result
