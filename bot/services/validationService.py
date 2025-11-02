import re
from typing import Optional, List
from utils.logger import botLogger


class ValidationService:
    @staticmethod
    def validateName(name: str) -> bool:
        if not name:
            return False
        value = name.strip()
        if len(value) < 2 or len(value) > 50:
            return False
        pattern = r'^[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\s\-]{1,49}$'
        return re.match(pattern, value) is not None

    @staticmethod
    def validateSurname(surname: str) -> bool:
        return ValidationService.validateName(surname)

    @staticmethod
    def validateClass(className: str) -> bool:
        if not className:
            return False
        pattern = r'^\d{1,2}\s*[А-ЯЁA-Z]?$'
        return re.match(pattern, className.strip(), re.IGNORECASE) is not None

    @staticmethod
    def validateAnswer(answer: str) -> bool:
        if not answer:
            return False
        answer = answer.strip()
        parts = answer.split()
        for part in parts:
            if not part.replace('.', '').replace('-', '').isdigit():
                return False
        return True

    @staticmethod
    def validateExamName(examName: str, availableExams: List[str]) -> Optional[str]:
        if not examName:
            return None
        examName = examName.strip()
        if examName in availableExams:
            return examName
        return None
