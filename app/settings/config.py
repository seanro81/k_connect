import os
import logging
from dotenv import load_dotenv

load_dotenv()

TOPIC_NAME = os.getenv('TOPIC_NAME')
KAFKA_SERVERS = os.getenv('KAFKA_SERVERS')

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

APP_PORT = int(os.getenv('APP_PORT'))

PG_CONN_STRING = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
