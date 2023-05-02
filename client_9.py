import traceback
from argparse import ArgumentParser
import os.path
from tools.config import prepare_config
import client, log

CONFIG_PATH = os.getenv("CONFIG_PATH", os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "config.json"))


def main():
    ap = ArgumentParser()
    ap.add_argument("addr", help="IP-address or 'localhost'")
    ap.add_argument("--port", dest="port", type=int, required=False, help="port in range 1024-49151")

    options = ap.parse_args()
    config = prepare_config(options, config_path=CONFIG_PATH, service="client")
    client = client(config)
    try:
        client.run()
    except Exception as e:
        log.critical(e.with_traceback(traceback.print_exc()), exc_info=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        log.critical(ex.with_traceback(traceback.print_exc()), exc_info=True)