import time

RESPONSE = {
    100: "неправильный объект JSON",
    101: "Отказано в доступе, вам необходимо войти в систему",
    102: '«неверный пароль» или «нет учетной записи с таким именем"',
    109: "Кто-то уже подключен с данным именем пользователя",
}


def error_400(error: str = None, code: int = 400) -> dict:
    if code in RESPONSE and error is None:
        error = RESPONSE[code]
    result = {
        "response": code,
        "time": time.time(),
    }
    if error is not None:
        result["error"] = error
    return result


def error_500(error: str = None, code: int = 500) -> dict:
    result = {
        "response": code,
        "time": time.time(),
    }
    if error is not None:
        result["error"] = error
    return result


def ok(msg: str = None, code: int = 200) -> dict:
    result = {
        "response": code
    }
    if msg is not None:
        result["alert"] = msg
    return result