from typing import Dict
from web3 import Web3
from eth_account import Account
from .config import settings

class BlockchainClient:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
        self.account = Account.from_key(settings.VALIDATOR_PRIVATE_KEY)
        
        # Загрузка ABI контракта (в реальном проекте нужно добавить)
        self.contract_abi = []  
        self.contract = self.w3.eth.contract(
            address=settings.CONTRACT_ADDRESS, 
            abi=self.contract_abi
        )

    def send_validation_to_contract(
        self,
        practice_id: int,
        rating_criteria: Dict[str, float],
        decision: str,
        stake_amount: int
    ):
        """
        Отправляет результаты валидации в смарт-контракт
        """
        try:
            # Подготовка транзакции
            tx = self.contract.functions.validatePractice(
                practice_id,
                int(rating_criteria['Q']),
                int(rating_criteria['R']),
                int(rating_criteria['U']),
                int(rating_criteria['A']),
                int(rating_criteria['I']),
                decision == 'approve',
                stake_amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            # Подписание и отправка транзакции
            signed_tx = self.w3.eth.account.sign_transaction(tx, settings.VALIDATOR_PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Ожидание подтверждения
            return self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
        except Exception as e:
            print(f"Ошибка при отправке валидации в блокчейн: {e}")
            raise 