import asyncio

from aiokafka import AIOKafkaConsumer
from settings.config import KAFKA_SERVERS
from aiokafka.errors import (
                               KafkaError,
                               ConsumerStoppedError,
                               IllegalStateError,
                               RecordTooLargeError,
                               UnsupportedVersionError)

from settings.config import logging
from adapters.pg import SimpleORM


async def kafka_init():
    aio_consumer = None
    AIO_KAFKA_CONSUMER_START = False
    try:
        aio_consumer = AIOKafkaConsumer('test-topic-app',
                                        bootstrap_servers=KAFKA_SERVERS,
                                        group_id='custom_metrics_consumer',
                                        enable_auto_commit=True,
                                        retry_backoff_ms=200
                                        )
        await aio_consumer.start()
        AIO_KAFKA_CONSUMER_START = True
    except (KafkaError, ConsumerStoppedError, IllegalStateError, RecordTooLargeError,
            UnsupportedVersionError) as ex:
        logging.error(f"KAFKA ERROR - {str(ex)}")
    finally:
        if aio_consumer and AIO_KAFKA_CONSUMER_START is False:
            await aio_consumer.stop()
            await asyncio.sleep(1)
    logging.info("KAFKA CONSUMER START")
    return aio_consumer, AIO_KAFKA_CONSUMER_START


async def consumer():
    aio_consumer = None
    AIO_KAFKA_CONSUMER_START = False

    while not AIO_KAFKA_CONSUMER_START:
        aio_consumer, start = await kafka_init()
        AIO_KAFKA_CONSUMER_START = start

    while True:
        try:
            async for msg in aio_consumer:
                logging.info(f"KAFKA GET NEW MESSAGE:{msg.value}")
                orm = SimpleORM()
                message = msg.value.decode("utf-8")
                await orm.metrics_register(json_data=message, metric_id='all')
        except Exception as ex:
            logging.error(f"KAFKA ERROR - {str(ex)}")
