"""Программа-сервер"""

import socket
import sys
import json
from constantsnutils import constants
from constantsnutils import utils


def process_client_message(message):
    if constants.ACTION in message and message[constants.ACTION] == constants.PRESENCE and constants.TIME in message \
            and constants.USER in message and message[constants.USER][constants.ACCOUNT_NAME] == 'Guest':
        return {constants.RESPONSE: 200}
    return {
        constants.RESPONSE: 400,
        constants.ERROR: 'Bad Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = constants.DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)


    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))


    transport.listen(constants.MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = utils.make_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            utils.send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Некорретное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()