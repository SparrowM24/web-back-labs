#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Инициализация таблицы films в базе данных"""
    
    print("=== Инициализация базы данных фильмов ===")
    
    try:
        # Подключаемся к БД
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', 5433)),
            database=os.getenv('DB_NAME', 'alice_dyachkova_knowledge_base2'),
            user=os.getenv('DB_USER', 'alice_dyachkova_knowledge_base'),
            password=os.getenv('DB_PASSWORD', '123456')
        )
        
        cursor = conn.cursor()
        
        # Читаем SQL-скрипт
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Выполняем SQL
        print("Создание таблицы films...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("✅ База данных успешно инициализирована!")
        
        # Проверяем
        cursor.execute("SELECT COUNT(*) FROM films")
        count = cursor.fetchone()[0]
        print(f"📊 Фильмов в базе: {count}")
        
        cursor.close()
        conn.close()
        
    except FileNotFoundError:
        print("❌ Файл database/schema.sql не найден!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    init_database()