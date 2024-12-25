from typing import Dict
from web3 import Web3
from eth_account import Account
from .config import settings
import logging

logger = logging.getLogger(__name__)

class BlockchainClient:
    def __init__(self):
        logger.info("Инициализация BlockchainClient (mock version)")
        
    def send_validation_to_contract(
        self,
        practice_id: str,
        rating_criteria: Dict[str, float],
        decision: str,
        stake_amount: int
    ):
        """
        Мок-версия отправки результатов валидации
        """
        logger.info(f"[MOCK] Отправка валидации в блокчейн:")
        logger.info(f"Practice ID: {practice_id}")
        logger.info(f"Ratings: {rating_criteria}")
        logger.info(f"Decision: {decision}")
        logger.info(f"Stake: {stake_amount}")
        
        return {
            "transactionHash": b"mock_tx_hash",
            "status": 1,
            "blockNumber": 1
        } 