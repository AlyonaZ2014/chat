import logging
import sys
import os.path
sys.path.append('../')
from common.constants import *


client_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'client.log')

steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(client_formatter)
steam.setLevel(logging.ERROR)
log_file = logging.FileHandler(path, encoding='utf8')
log_file.setFormatter(client_formatter)

logger = logging.getLogger('client')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error ivent')
    logger.debug('Test debug ivent')
    logger.info('Test info ivent')













# logger = logging.getLogger('chat.client')


# storage_log = 'log-storage'
# if not os.path.exists(storage_log):
#     os.mkdir(storage_log)
# file_name = os.path.join(storage_log, 'chat.client.log')

# formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s ")

# file_han = logging.FileHandler(file_name, encoding='utf-8')
# file_han .setLevel(logging.DEBUG)
# file_han .setFormatter(formatter)

# logger.addHandler(file_han)
# logger.setLevel(logging.DEBUG)
# logge = logging.getLogger('client')

# if __name__ == '__main__':
#     console = logging.StreamHandler()
#     console.setLevel(logging.DEBUG)
#     console.setFormatter(formatter)
#     logger.addHandler(console)
#     logger.info('Тест логирования')