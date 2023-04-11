"""Программа-клиент"""
import json
import sys
import socket
import time
import constants
import utils


def client_presence(account_name='Guest'):
    out = {
        constants.ACTION: constants.PRESENCE,
        constants.TIME: time.time(),
        constants.USER: {
            constants.ACCOUNT_NAME: account_name
        }
    }
    return out


def process_answer(message):
    if constants.RESPONSE in message:
        if message[constants.RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[constants.ERROR]}'
    raise ValueError


def main():
    try:
        server_address = sys.argv[0]
        server_port = int(sys.argv[0])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = constants.DEFAULT_IP_ADDRESS
        server_port = constants.DEFAULT_PORT
    except ValueError:
        print('В диапазоне порта может быть число от 1024 до 65535.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = client_presence()
    utils.send_message(transport, message_to_server)
    try:
        answer = process_answer(utils.make_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Сообщение сервера не декодировать')


if __name__ == '__main__':
    main()