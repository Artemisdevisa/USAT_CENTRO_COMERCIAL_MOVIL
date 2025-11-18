import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # ==========================================
    # CONFIGURACIÓN DE BASE DE DATOS
    # ==========================================
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'cceliasa')
    DB_PORT = int(os.environ.get('DB_PORT', 5432))
    
    # ==========================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    
    # ==========================================
    # CONFIGURACIÓN DE CLOUDINARY (HARDCODED)
    # ==========================================
    CLOUDINARY_CLOUD_NAME = 'dlr3o09q0'  # ← dlr (con L)
    CLOUDINARY_API_KEY = '375591668928889'
    CLOUDINARY_API_SECRET = '5u3OfMWZEoCNfp5HvwmvrI_Zjuk'
    
    @staticmethod
    def print_config():
        """Debug: Imprimir configuración (sin password ni secrets)"""
        print("=" * 50)
        print("🔧 CONFIGURACIÓN DEL SISTEMA")
        print("=" * 50)
        print(f"📊 DB_HOST: {Config.DB_HOST}")
        print(f"👤 DB_USER: {Config.DB_USER}")
        print(f"🗄️  DB_NAME: {Config.DB_NAME}")
        print(f"🔌 DB_PORT: {Config.DB_PORT}")
        print(f"☁️  CLOUDINARY: {Config.CLOUDINARY_CLOUD_NAME}")
        print("=" * 50)

# ==========================================
# CONFIGURAR CLOUDINARY AL CARGAR EL MÓDULO
# ==========================================
try:
    cloudinary.config(
        cloud_name='dlr3o09q0',  # ← dlr (con L)
        api_key='375591668928889',
        api_secret='5u3OfMWZEoCNfp5HvwmvrI_Zjuk',
        secure=True
    )
    print(f"✅ Cloudinary configurado: dlr3o09q0")
except Exception as e:
    print(f"⚠️ Error al configurar Cloudinary: {e}")