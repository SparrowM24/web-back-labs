"""
Универсальное подключение к базе данных
"""

import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Универсальная функция подключения к базе данных.
    
    Приоритет:
    1. Переменные окружения из .env файла
    2. Значения по умолчанию для KOMPAS-3D (ваша локальная разработка)
    
    Для использования в других средах создайте файл .env с нужными параметрами.
    """
    try:
        # Пробуем получить параметры из переменных окружения
        host = os.getenv('DB_HOST', '127.0.0.1')
        port = int(os.getenv('DB_PORT', 5433))
        database = os.getenv('DB_NAME', 'alice_dyachkova_knowledge_base2')
        user = os.getenv('DB_USER', 'alice_dyachkova_knowledge_base')
        password = os.getenv('DB_PASSWORD', '123456')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            cursor_factory=DictCursor
        )
        return conn
        
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Используются значения по умолчанию для KOMPAS-3D")
        raise