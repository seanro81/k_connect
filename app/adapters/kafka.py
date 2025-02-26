
async def kafka_init(loop):
    aio_consumer = None
    AIO_KAFKA_CONSUMER_START = False
    try:
        aio_consumer = AIOKafkaConsumer(AUDIT_SUBSCRIBER['topic'], loop=loop,
                                        bootstrap_servers=[AUDIT_SUBSCRIBER['servers']],
                                        group_id=AUDIT_SUBSCRIBER['group_id'],
                                        enable_auto_commit=True,
                                        retry_backoff_ms=AUDIT_SUBSCRIBER['retry_backoff_ms']
                                        )
        await aio_consumer.start()
        AIO_KAFKA_CONSUMER_START = True
    except (KafkaError, ConsumerStoppedError, IllegalOperation, IllegalStateError, RecordTooLargeError,
            UnsupportedVersionError) as ex:
        logger.error(lf.add_event().msg(f"audit_consumer_task: SFDO KAFKA ERROR - {str(ex)}").status_('ERROR').
                     error(trace=str(ex), code='SFDO').dict())
    finally:
        if aio_consumer and AIO_KAFKA_CONSUMER_START is False:
            await aio_consumer.stop()
            await asyncio.sleep(AUDIT_SUBSCRIBER['wait_on_error'])
    logger.info(lf.add_event().msg("audit_consumer_task:  SFDO KAFKA consumer start").dict())
    return aio_consumer, AIO_KAFKA_CONSUMER_START


async def consumer(loop):
    aio_consumer = None
    AIO_KAFKA_CONSUMER_START = False

    while not AIO_KAFKA_CONSUMER_START:
        aio_consumer, start = await kafka_init_(loop=loop)
        AIO_KAFKA_CONSUMER_START = start

    while True:
        log = lf.add_event()
        try:
            async for msg in aio_consumer:
                log = lf.add_event()
                await get_new_message(msg=msg,log=log,loop=loop)
                # допилить лог и передать или вернуть актуально событие лога
        except Exception as ex:
            logger.error(log.msg(f'audit_consumer_task: error {str(ex)}').status_('ERROR').error(trace=str(ex),
                                                                                                 code='AUDIT.100').dict())