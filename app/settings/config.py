import os
import logging
from dotenv import load_dotenv

load_dotenv()


TOPIC_NAME = os.getenv('TOPIC_NAME')
KAFKA_SERVERS = os.getenv('KAFKA_SERVERS')

PUBLISHER_SLEEP_SEC = int(os.getenv('PUBLISHER_SLEEP_SEC'))
WORK_BEFORE_BREAK_SEC = int(os.getenv('WORK_BEFORE_BREAK_SEC'))


format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")



PG_CONN_STRING = 'postgresql://postgres@localhost/test'