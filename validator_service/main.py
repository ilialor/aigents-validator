async def setup_rabbitmq():
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS
    )
    
    channel = await connection.channel()
    
    # Объявляем exchange
    exchange = await channel.declare_exchange(
        "practice.exchange",
        type="topic",
        durable=True
    )
    
    # Объявляем очередь
    queue = await channel.declare_queue(
        "practice.events",
        durable=True
    )
    
    # Привязываем очередь к exchange
    await queue.bind(
        exchange=exchange,
        routing_key="practice.*"  # Слушаем все события практик
    )
    
    logger.info(f"Подключились к RabbitMQ: {settings.RABBITMQ_HOST}")
    logger.info("Объявили exchange practice.exchange")
    logger.info("Объявили очередь practice.events")
    logger.info("Привязали очередь к exchange с routing_key practice.*")
    
    return connection, queue 