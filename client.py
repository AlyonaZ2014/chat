import sys
import json
import socket
import time
import argparse
import logging
from log import client_log_config
from common.constants import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, IncorrectDataRecivedError, ServerError
from decos import log
from common.utils import get_message, send_message

LOGGER = logging.getLogger('client')

@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOGGER.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def process_response_ans(message):
    LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    print('Консольный месседжер. Клиентский модуль.')

    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()


# @log
# def message_from_server(message):
#     if ACTION in message and message[ACTION] == MESSAGE and \
#             SENDER in message and MESSAGE_TEXT in message:
#         print(f'Получено сообщение от пользователя '
#               f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
#         LOGGER.info(f'Получено сообщение от пользователя '
#                     f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
#     else:
#         LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


# @log
# def create_message(sock, account_name='Guest'):
#     message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
#     if message == '!!!':
#         sock.close()
#         LOGGER.info('Завершение работы по команде пользователя.')
#         print('Спасибо за использование нашего сервиса!')
#         sys.exit(0)
#     message_dict = {
#         ACTION: MESSAGE,
#         TIME: time.time(),
#         ACCOUNT_NAME: account_name,
#         MESSAGE_TEXT: message
#     }
#     LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
#     return message_dict


# @log
# def create_presence(account_name='Guest'):
#     out = {
#         ACTION: PRESENCE,
#         TIME: time.time(),
#         USER: {
#             ACCOUNT_NAME: account_name
#         }
#     }
#     LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
#     return out


# @log
# def process_response_ans(message):
#     LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
#     if RESPONSE in message:
#         if message[RESPONSE] == 200:
#             return '200 : OK'
#         elif message[RESPONSE] == 400:
#             raise ServerError(f'400 : {message[ERROR]}')
#     raise ReqFieldMissingError(RESPONSE)


# @log
# def arg_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
#     parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
#     parser.add_argument('-m', '--mode', default='listen', nargs='?')
#     namespace = parser.parse_args(sys.argv[1:])
#     server_address = namespace.addr
#     server_port = namespace.port
#     client_mode = namespace.mode

#     if not 1023 < server_port < 65536:
#         LOGGER.critical(
#             f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
#             f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
#         sys.exit(1)

#     if client_mode not in ('listen', 'send'):
#         LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
#                         f'допустимые режимы: listen , send')
#         sys.exit(1)

#     return server_address, server_port, client_mode


# def main():
#     server_address, server_port, client_mode = arg_parser()

#     LOGGER.info(
#         f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
#         f'порт: {server_port}, режим работы: {client_mode}')

#     try:
#         transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         transport.connect((server_address, server_port))
#         send_message(transport, create_presence())
#         answer = process_response_ans(get_message(transport))
#         LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
#         print(f'Установлено соединение с сервером.')
#     except json.JSONDecodeError:
#         LOGGER.error('Не удалось декодировать полученную Json строку.')
#         sys.exit(1)
#     except ServerError as error:
#         LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
#         sys.exit(1)
#     except ReqFieldMissingError as missing_error:
#         LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
#         sys.exit(1)
#     except ConnectionRefusedError:
#         LOGGER.critical(
#             f'Не удалось подключиться к серверу {server_address}:{server_port}, '
#             f'конечный компьютер отверг запрос на подключение.')
#         sys.exit(1)
#     else:
#         # Если соединение с сервером установлено корректно,
#         # начинаем обмен с ним, согласно требуемому режиму.
#         # основной цикл прогрммы:
#         if client_mode == 'send':
#             print('Режим работы - отправка сообщений.')
#         else:
#             print('Режим работы - приём сообщений.')
#         while True:
#             # режим работы - отправка сообщений
#             if client_mode == 'send':
#                 try:
#                     send_message(transport, create_message(transport))
#                 except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
#                     LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
#                     sys.exit(1)

#             # Режим работы приём:
#             if client_mode == 'listen':
#                 try:
#                     message_from_server(get_message(transport))
#                 except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
#                     LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
#                     sys.exit(1)


# if __name__ == '__main__':
#     main()

