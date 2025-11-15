import os

class Config:
    # Base de datos
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'cceliasa')
    DB_PORT = int(os.environ.get('DB_PORT', 5432))
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    
    @staticmethod
    def print_config():
        """Debug: Imprimir configuración (sin password)"""
        print(f"🔧 DB_HOST: {Config.DB_HOST}")
        print(f"🔧 DB_USER: {Config.DB_USER}")
        print(f"🔧 DB_NAME: {Config.DB_NAME}")
        print(f"🔧 DB_PORT: {Config.DB_PORT}")