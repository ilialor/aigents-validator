import json
import pika
import requests
from typing import Dict
import logging

from .config import settings
from .ai_agent import analyze_practice
from .blockchain import BlockchainClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidatorConsumer:
    def __init__(self):
        self.blockchain_client = BlockchainClient()
        self.connect_to_rabbitmq()

    def connect_to_rabbitmq(self):
        """Установка соединения с RabbitMQ"""
        try:
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
                routing_key='practice.created'  # Конкретный routing key для события создания практики
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

    def get_practice_details(self, practice_id: str) -> Dict:
        """Получение деталей практики через FastAPI"""
        try:
            url = f"{settings.FASTAPI_URL}/api/v1/practices/{practice_id}"
            logger.info(f"Fetching practice details from: {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            logger.info(f"Successfully retrieved practice details for ID: {practice_id}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching practice details: {e}")
            raise

    def process_message(self, ch, method, properties, body):
        """Обработка сообщения из очереди"""
        try:
            event_data = json.loads(body)
            
            # Проверяем тип события
            if event_data.get('type') == 'practice.created':
                practice_id = event_data['payload']['practice_id']
                
                logger.info(f"Получено новое сообщение для практики {practice_id}")
                
                # Получаем полные данные практики
                full_practice_data = self.get_practice_details(practice_id)
                
                # Анализируем практику через AI-агента
                rating_criteria = analyze_practice(full_practice_data)
                
                # Принимаем решение на основе sota_score
                final_decision = 'approve' if rating_criteria['sota_score'] > 5 else 'reject'
                stake_amount = 100  # Фиксированный стейк для MVP
                
                # Отправляем результаты в блокчейн
                tx_receipt = self.blockchain_client.send_validation_to_contract(
                    practice_id,
                    rating_criteria,
                    final_decision,
                    stake_amount
                )
                
                logger.info(f"Валидация успешно записана в блокчейн. TX: {tx_receipt['transactionHash'].hex()}")
                
                # Подтверждаем обработку сообщения
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            # В случае ошибки возвращаем сообщение в очередь
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Запуск консьюмера"""
        try:
            logger.info("Запуск Validator Service...")
            
            # Настраиваем получение сообщений
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='practice.events',
                on_message_callback=self.process_message,
                auto_ack=False
            )
            
            logger.info("Ожидание сообщений из очереди practice.events...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки, закрываем соединение...")
            self.connection.close()
            
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            raise

if __name__ == "__main__":
    consumer = ValidatorConsumer()
    consumer.start() 