from socket import socket
from unittest import TestCase, main

import sys
import os

dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(dir)

from server import main, process_client_message


class TestServer(TestCase):

    def test_main(self):
        s = main(1026)
        self.assertEqual(type(s), socket)

    def test_process_client_message(self):
        result = process_client_message(response_code=200)
        self.assertEqual(type(result), bytes)


if __name__ == '__main__':
    main()