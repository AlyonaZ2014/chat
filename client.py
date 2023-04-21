import sys
import json
import socket
import time
import argparse
import logging
from log import client_log_config
from common import constants
from common import utils
from errors import ReqFieldMissingError
from decos import log

LOGGER = logging.getLogger('client')


@log
def create_presence(account_name='Guest'):
    out = {
        constants.ACTION: constants.PRESENCE,
        constants.TIME: time.time(),
        constants.USER: {
            constants.ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {constants.PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_ans(message):
    LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if constants.RESPONSE in message:
        if message[constants.RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[constants.ERROR]}'
    raise ReqFieldMissingError(constants.RESPONSE)


@log
def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=constants.DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=constants.DEFAULT_PORT, type=int, nargs='?')
    return parser


def main():
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    LOGGER.info(f'Запущен клиент с парамертами: адрес сервера: '
                f'{server_address}, порт: {server_port}')
    
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        utils.send_message(transport, message_to_server)
        answer = process_ans(utils.get_message(transport))
        LOGGER.info(f'Принят ответ от сервера {answer}')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    main()
