import sys
import os
import unittest
import json

from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message

sys.path.append(os.path.join(os.getcwd(), '..'))

class connect:

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.receved_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    test_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'hello_Al'
        }
    }
    test_recv_ok = {RESPONSE: 200}
    test_recv_err = {
        RESPONSE: 400,
        ERROR: 'bay_Al'
    }

    def test_send_message(self):
        test_socket = connect(self.test_send)
        send_message(test_socket, self.test_send)
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        test_sock_ok = connect(self.test_recv_ok)
        test_sock_err = connect(self.test_recv_err)
        self.assertEqual(get_message(test_sock_ok), self.test_recv_ok)
        self.assertEqual(get_message(test_sock_err), self.test_recv_err)


if __name__ == '__main__':
    unittest.main()
