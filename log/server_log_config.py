import logging
import logging.handlers
import os.path

logger = logging.getLogger('chat.server')


storage_log = 'log-storage'
if not os.path.exists(storage_log):
    os.mkdir(storage_log)
file_name = os.path.join(storage_log, 'chat.server.log')

formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s ")

file_han = logging.handlers.TimedRotatingFileHandler(file_name, encoding='utf-8', when='D', interval=1, backupCount=7)
file_han.setLevel(logging.DEBUG)
file_han.setFormatter(formatter)

logger.addHandler(file_han)
logger.setLevel(logging.DEBUG)
logge = logging.getLogger('client')

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.info('Тест логирования')