import json
import pika
import requests
import asyncio
from typing import Dict, Any, Optional
import logging
from aio_pika import IncomingMessage, connect_robust
from aio_pika.abc import AbstractRobustConnection
import backoff

from .config import settings
from .ai_agent import analyze_practice, AnalysisResult
from .blockchain import BlockchainClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageConsumer:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.loop = loop or asyncio.get_event_loop()
        self.blockchain = BlockchainClient()
        self.connection = None
        self.channel = None
        
    def _on_message(self, channel, method_frame, header_frame, body):
        """Обертка для обработки входящего сообщения"""
        try:
            if self.connection is None or self.connection.is_closed:
                logger.error("Connection is closed, reconnecting...")
                self.connect_to_rabbitmq()
            self.process_message(channel, method_frame, header_frame, body)
        except Exception as e:
            logger.error(f"Error in message wrapper: {str(e)}")
            if not channel.is_closed:
                channel.basic_reject(delivery_tag=method_frame.delivery_tag)
        
    def process_message(self, ch, method, properties, body):
        """Обработка входящего сообщения"""
        try:
            # Декодируем сообщение
            data = json.loads(body.decode())
            logger.debug(f"Received message: {data}")
            
            # Получаем practice_id из payload
            practice_id = data.get("payload", {}).get("practice_id")
            if not practice_id:
                logger.error("No practice_id in message payload")
                logger.debug(f"Message structure: {data}")
                ch.basic_reject(delivery_tag=method.delivery_tag)
                return
                
            logger.info(f"Received new message for practice {practice_id}")
            
            # Получаем данные практики из API
            full_practice_data = self.get_practice_details(practice_id)
            if not full_practice_data:
                logger.error(f"Failed to fetch practice data for {practice_id}")
                ch.basic_reject(delivery_tag=method.delivery_tag)
                return
                
            # Создаем новый event loop для асинхронных операций
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Анализируем практику
                analysis_result = loop.run_until_complete(analyze_practice(full_practice_data))
                
                # Проверяем результат
                if not analysis_result or "sota_score" not in analysis_result:
                    logger.error(f"Invalid analysis result for practice {practice_id}")
                    ch.basic_reject(delivery_tag=method.delivery_tag)
                    return
                    
                # Отправляем результат в блокчейн
                tx_result = loop.run_until_complete(self.blockchain.send_validation_to_contract(
                    practice_id=practice_id,
                    scores=analysis_result["scores"],
                    sota_score=analysis_result["sota_score"],
                    reliability_score=analysis_result.get("reliability_score", 0.0)
                ))
            finally:
                loop.close()
            
            if tx_result and tx_result["status"] == 1:
                logger.info(f"Successfully validated practice {practice_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.error(f"Failed to send validation to blockchain for practice {practice_id}")
                ch.basic_reject(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            if not ch.is_closed:
                ch.basic_reject(delivery_tag=method.delivery_tag)

    @backoff.on_exception(backoff.expo, 
                         (requests.exceptions.RequestException,),
                         max_tries=3)
    def get_practice_details(self, practice_id: str) -> Dict:
        """Получение деталей практики через FastAPI с автоматическим повтором при ошибке"""
        try:
            url = f"{settings.FASTAPI_URL}/api/v1/practices/{practice_id}"
            logger.info(f"Fetching practice details from: {url}")
            
            response = requests.get(url, timeout=10)  # Добавляем timeout
            response.raise_for_status()
            
            logger.info(f"Successfully retrieved practice details for ID: {practice_id}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching practice details: {e}")
            raise

    @backoff.on_exception(backoff.expo, 
                         (pika.exceptions.AMQPConnectionError,
                          pika.exceptions.AMQPChannelError),
                         max_tries=5)
    def connect_to_rabbitmq(self):
        """Установка соединения с RabbitMQ с автоматическим повтором при ошибке"""
        try:
            if self.connection and not self.connection.is_closed:
                return
                
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER, 
                settings.RABBITMQ_PASS
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info("Подключились к RabbitMQ")
            
            # Объявляем exchange
            self.channel.exchange_declare(
                exchange='practice.exchange',
                exchange_type='topic',
                durable=True
            )
            logger.info("Объявили exchange: practice.exchange")
            
            # Объявляем очередь
            result = self.channel.queue_declare(
                queue='practice.events', 
                durable=True
            )
            logger.info(f"Объявили очередь: practice.events, {result.method.message_count} сообщений в очереди")
            
            # Создаем привязку
            self.channel.queue_bind(
                exchange='practice.exchange',
                queue='practice.events',
                routing_key='practice.created'
            )
            logger.info("Создали привязку: practice.events -> practice.exchange (practice.created)")
            
            # Дополнительная привязка для всех событий практик
            self.channel.queue_bind(
                exchange='practice.exchange',
                queue='practice.events',
                routing_key='practice.*'
            )
            logger.info("Создали привязку: practice.events -> practice.exchange (practice.*)")
            
        except Exception as e:
            logger.error(f"Ошибка при подключении к RabbitMQ: {e}", exc_info=True)
            raise

    def start(self):
        """Запуск консьюмера"""
        while True:
            try:
                if self.connection is None or self.connection.is_closed:
                    self.connect_to_rabbitmq()
                
                logger.info("Запуск Validator Service...")
                
                # Настраиваем получение сообщений
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(
                    queue='practice.events',
                    on_message_callback=self._on_message,
                    auto_ack=False
                )
                
                logger.info("Ожидание сообщений из очереди practice.events...")
                self.channel.start_consuming()
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки, закрываем соединение...")
                if self.connection and not self.connection.is_closed:
                    self.connection.close()
                break
                
            except pika.exceptions.AMQPConnectionError:
                logger.error("Потеряно соединение с RabbitMQ, пробуем переподключиться...")
                continue
                
            except Exception as e:
                logger.error(f"Критическая ошибка: {e}")
                if self.connection and not self.connection.is_closed:
                    self.connection.close()
                raise

if __name__ == "__main__":
    consumer = MessageConsumer()
    consumer.start() 