from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RABBITMQ_HOST: str = "events-rabbitmq-1"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "aigents" 
    RABBITMQ_PASS: str = "aigents_secret"  
    
    FASTAPI_URL: str = "http://fastapi:8000"
    
    # Настройки Web3
    WEB3_PROVIDER_URI: str = "http://localhost:8545"
    VALIDATOR_PRIVATE_KEY: str = ""
    CONTRACT_ADDRESS: str = ""
    
    # Переименовываем переменные в верхний регистр
    POLYGON_RPC_URL: str
    POLYGON_PRIVATE_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 