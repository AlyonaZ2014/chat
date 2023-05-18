import socket
import sys
import argparse
import select
import json
import time
import logger
import logging
import threading
import log.server_log_config
from errors import IncorrectDataRecivedError
from common.constants import *
from common.utils import get_message, send_message
from decos import log
from descrptrs import Port
from metaclasses import ServerMaker
from server_database import ServerStorage

LOGGER = logging.getLogger('server')

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port

# Основной класс сервера
class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # База данных сервера
        self.database = database

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

        # Конструктор предка
        super().__init__()

    def init_socket(self):
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen()

    def run(self):
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
    # пользователей и слушающие сокеты. Ничего не возвращает.
    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, отправляет
    #     словарь-ответ в случае необходимости.
    def process_client_message(self, message, client):
        logger.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port = arg_parser()

    # Инициализация базы данных
    database = ServerStorage()

    # Создание экземпляра класса - сервера и его запуск:
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Печатаем справку:
    print_help()

    # Основной цикл сервера:
    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()















# # Основной класс сервера
# class Server(metaclass=ServerMaker):
#     port = Port()

#     def __init__(self, listen_address, listen_port):
#         # Параментры подключения
#         self.addr = listen_address
#         self.port = listen_port

#         # Список подключённых клиентов.
#         self.clients = []

#         # Список сообщений на отправку.
#         self.messages = []

#         # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
#         self.names = dict()

#     def init_socket(self):
#         logger.info(
#             f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
#         # Готовим сокет
#         transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         transport.bind((self.addr, self.port))
#         transport.settimeout(0.5)

#         # Начинаем слушать сокет.
#         self.sock = transport
#         self.sock.listen()

#     def main_loop(self):
#         # Инициализация Сокета
#         self.init_socket()

#         # Основной цикл программы сервера
#         while True:
#             # Ждём подключения, если таймаут вышел, ловим исключение.
#             try:
#                 client, client_address = self.sock.accept()
#             except OSError:
#                 pass
#             else:
#                 logger.info(f'Установлено соедение с ПК {client_address}')
#                 self.clients.append(client)

#             recv_data_lst = []
#             send_data_lst = []
#             err_lst = []
#             # Проверяем на наличие ждущих клиентов
#             try:
#                 if self.clients:
#                     recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
#             except OSError:
#                 pass

#             # принимаем сообщения и если ошибка, исключаем клиента.
#             if recv_data_lst:
#                 for client_with_message in recv_data_lst:
#                     try:
#                         self.process_client_message(get_message(client_with_message), client_with_message)
#                     except:
#                         logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
#                         self.clients.remove(client_with_message)

#             # Если есть сообщения, обрабатываем каждое.
#             for message in self.messages:
#                 try:
#                     self.process_message(message, send_data_lst)
#                 except:
#                     logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
#                     self.clients.remove(self.names[message[DESTINATION]])
#                     del self.names[message[DESTINATION]]
#             self.messages.clear()

#     # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
#     # пользователей и слушающие сокеты. Ничего не возвращает.
#     def process_message(self, message, listen_socks):
#         if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
#             send_message(self.names[message[DESTINATION]], message)
#             logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
#         elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
#             raise ConnectionError
#         else:
#             logger.error(
#                 f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

#     # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, отправляет
#     #     словарь-ответ в случае необходимости.
#     def process_client_message(self, message, client):
#         logger.debug(f'Разбор сообщения от клиента : {message}')
#         # Если это сообщение о присутствии, принимаем и отвечаем
#         if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
#             # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.
#             if message[USER][ACCOUNT_NAME] not in self.names.keys():
#                 self.names[message[USER][ACCOUNT_NAME]] = client
#                 send_message(client, RESPONSE_200)
#             else:
#                 response = RESPONSE_400
#                 response[ERROR] = 'Имя пользователя уже занято.'
#                 send_message(client, response)
#                 self.clients.remove(client)
#                 client.close()
#             return
#         # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
#         elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
#                 and SENDER in message and MESSAGE_TEXT in message:
#             self.messages.append(message)
#             return
#         # Если клиент выходит
#         elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
#             self.clients.remove(self.names[ACCOUNT_NAME])
#             self.names[ACCOUNT_NAME].close()
#             del self.names[ACCOUNT_NAME]
#             return
#         # Иначе отдаём Bad request
#         else:
#             response = RESPONSE_400
#             response[ERROR] = 'Запрос некорректен.'
#             send_message(client, response)
#             return


# def main():
#     # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
#     listen_address, listen_port = arg_parser()

#     # Создание экземпляра класса - сервера.
#     server = Server(listen_address, listen_port)
#     server.main_loop()


# if __name__ == '__main__':
#     main()












# @log
# def process_client_message(message, messages_list, client, clients, names):
#     LOGGER.debug(f'Разбор сообщения от клиента : {message}')
#     if ACTION in message and message[ACTION] == PRESENCE and \
#             TIME in message and USER in message:
#         if message[USER][ACCOUNT_NAME] not in names.keys():
#             names[message[USER][ACCOUNT_NAME]] = client
#             send_message(client, RESPONSE_200)
#         else:
#             response = RESPONSE_400
#             response[ERROR] = 'Имя пользователя уже занято.'
#             send_message(client, response)
#             clients.remove(client)
#             client.close()
#         return
#     elif ACTION in message and message[ACTION] == MESSAGE and \
#             DESTINATION in message and TIME in message \
#             and SENDER in message and MESSAGE_TEXT in message:
#         messages_list.append(message)
#         return
#     elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
#         clients.remove(names[message[ACCOUNT_NAME]])
#         names[message[ACCOUNT_NAME]].close()
#         del names[message[ACCOUNT_NAME]]
#         return
#     else:
#         response = RESPONSE_400
#         response[ERROR] = 'Запрос некорректен.'
#         send_message(client, response)
#         return


# @log
# def process_message(message, names, listen_socks):
#     if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
#         send_message(names[message[DESTINATION]], message)
#         LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
#                     f'от пользователя {message[SENDER]}.')
#     elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
#         raise ConnectionError
#     else:
#         LOGGER.error(
#             f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
#             f'отправка сообщения невозможна.')


# @log
# def arg_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
#     parser.add_argument('-a', default='', nargs='?')
#     namespace = parser.parse_args(sys.argv[1:])
#     listen_address = namespace.a
#     listen_port = namespace.p
    
#     if not 1023 < listen_port < 65536:
#         LOGGER.critical(
#             f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. '
#             f'Допустимы адреса с 1024 до 65535.')
#         sys.exit(1)

#     return listen_address, listen_port




# def main():
#     listen_address, listen_port = arg_parser()

#     LOGGER.info(
#         f'Запущен сервер, порт для подключений: {listen_port}, '
#         f'адрес с которого принимаются подключения: {listen_address}. '
#         f'Если адрес не указан, принимаются соединения с любых адресов.')
#     transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     transport.bind((listen_address, listen_port))
#     transport.settimeout(0.5)

#     clients = []
#     messages = []

#     names = dict()

#     transport.listen(MAX_CONNECTIONS)
#     while True:
#         try:
#             client, client_address = transport.accept()
#         except OSError:
#             pass
#         else:
#             LOGGER.info(f'Установлено соедение с ПК {client_address}')
#             clients.append(client)

#         recv_data_lst = []
#         send_data_lst = []
#         err_lst = []
#         try:
#             if clients:
#                 recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
#         except OSError:
#             pass

#         if recv_data_lst:
#             for client_with_message in recv_data_lst:
#                 try:
#                     process_client_message(get_message(client_with_message),
#                                            messages, client_with_message, clients, names)
#                 except Exception:
#                     LOGGER.info(f'Клиент {client_with_message.getpeername()} '
#                                 f'отключился от сервера.')
#                     clients.remove(client_with_message)

#         for i in messages:
#             try:
#                 process_message(i, names, send_data_lst)
#             except Exception:
#                 LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
#                 clients.remove(names[i[DESTINATION]])
#                 del names[i[DESTINATION]]
#         messages.clear()


# if __name__ == '__main__':
#     main()

