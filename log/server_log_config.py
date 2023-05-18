import sys
import logging
import logging.handlers
import os.path
from common.constants import LOGGING_LEVEL


server_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'server.log')

steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(server_formatter)
steam.setLevel(logging.INFO)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='D')
log_file.setFormatter(server_formatter)

logger = logging.getLogger('server')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error ivent')
    logger.debug('Test debug ivent')
    logger.info('Test info ivent')







# logger = logging.getLogger('chat.server')


# storage_log = 'log-storage'
# if not os.path.exists(storage_log):
#     os.mkdir(storage_log)
# file_name = os.path.join(storage_log, 'chat.server.log')

# formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s ")

# file_han = logging.handlers.TimedRotatingFileHandler(file_name, encoding='utf-8', when='D', interval=1, backupCount=7)
# file_han.setLevel(logging.DEBUG)
# file_han.setFormatter(formatter)

# logger.addHandler(file_han)
# logger.setLevel(logging.DEBUG)
# logge = logging.getLogger('client')

# if __name__ == '__main__':
#     console = logging.StreamHandler()
#     console.setLevel(logging.DEBUG)
#     console.setFormatter(formatter)
#     logger.addHandler(console)
#     logger.info('Тест логирования 2')