#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилита для перераспределения товаров из файла 'other' по категориям
на основе обновленного файла ключевых слов.
"""

import json
import os
import sys
from collections import defaultdict
import logging

# --- Исправление импорта для запуска из командной строки ---
try:
    # Попытка относительного импорта, когда скрипт - часть пакета
    from .categorization import categorize_product
    from .lemmatizer import lemmatize_text # Нужен для определения языка
except ImportError:
    # Фолбэк для прямого запуска: добавляем родительскую директорию в sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.categorization import categorize_product
    from utils.lemmatizer import lemmatize_text

def load_keywords(keywords_file):
    """Загружает ключевые слова из файла."""
    if not os.path.exists(keywords_file):
        logging.error(f"Файл ключевых слов не найден: {keywords_file}")
        return None
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки ключевых слов: {e}")
        return None

def load_products_from_file(file_path):
    """Загружает товары из файла."""
    if not os.path.exists(file_path):
        # Это нормальная ситуация, если файл категории еще не создан
        logging.warning(f"Файл не найден, будет создан новый: {os.path.basename(file_path)}")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        logging.error(f"Ошибка чтения файла {file_path}: {e}")
        return []

def save_products_to_file(products, file_path):
    """Сохраняет список товаров в файл, перезаписывая его."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(products) + '\n')
        return True
    except Exception as e:
        logging.error(f"Ошибка записи в файл {file_path}: {e}")
        return False

def append_products_to_file(products, file_path):
    """Добавляет товары в файл, избегая дубликатов."""
    existing_products = set(load_products_from_file(file_path))
    new_products = [p for p in products if p not in existing_products]
    
    if not new_products:
        return 0
        
    all_products = sorted(list(existing_products.union(set(new_products))))
    save_products_to_file(all_products, file_path)
    return len(new_products)

def redistribute_products(other_file_path, keywords_file, lang='uk'):
    """
    Перераспределяет товары из файла OTHER.
    """
    logging.info("🔄 Начинаю перераспределение товаров из OTHER...")
    
    keywords_data = load_keywords(keywords_file)
    if not keywords_data:
        return False

    products = load_products_from_file(other_file_path)
    if not products:
        logging.warning("Файл OTHER пуст или не найден. Нечего перераспределять.")
        return False

    logging.info(f"Загружено {len(products)} товаров из {os.path.basename(other_file_path)}")

    # Группируем товары по новым категориям
    newly_categorized = defaultdict(list)
    remaining_in_other = []
    
    for product in products:
        # Определяем категорию с учетом языка
        subcategory = categorize_product(product, keywords_data, lang)
        if subcategory != 'other':
            newly_categorized[subcategory].append(product)
        else:
            remaining_in_other.append(product)

    if not newly_categorized:
        logging.info("Не найдено товаров для перераспределения с новыми ключами.")
        return True

    logging.info("📊 Статистика перераспределения:")
    total_redistributed = 0
    output_dir = os.path.dirname(other_file_path)
    
    # Извлекаем префикс из имени файла, например "rozetka_alcohol_"
    base_filename = os.path.basename(other_file_path).replace('_other.txt', '')

    for subcategory, prods in newly_categorized.items():
        total_redistributed += len(prods)
        logging.info(f"  -> Категория '{subcategory}': {len(prods)} товаров")
        
        # Формируем имя файла на основе оригинала
        target_filename = f"{base_filename}_{subcategory}.txt"
        target_filepath = os.path.join(output_dir, target_filename)
        
        added_count = append_products_to_file(prods, target_filepath)
        logging.info(f"     Добавлено {added_count} новых товаров в {target_filename}")

    # Обновляем исходный файл OTHER
    logging.info(f"🗑️ Обновляю {os.path.basename(other_file_path)}...")
    save_products_to_file(remaining_in_other, other_file_path)
    
    logging.info(f"\n🎉 Перераспределение завершено!")
    logging.info(f"📦 Всего перераспределено: {total_redistributed} товаров.")
    logging.info(f"📁 Осталось в OTHER: {len(remaining_in_other)} товаров.")
    
    return True

def main():
    """
    Основная функция для запуска из командной строки.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M')
    
    # Определяем пути относительно расположения скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '..') # finpi_scraper/

    # TODO: Сделать выбор файла более гибким, через аргументы командной строки
    other_file = os.path.join(base_dir, "output/GOODS/GROCERIES/BEVERAGES/rozetka_alcohol_other.txt")
    keywords_file = os.path.join(base_dir, "keywords/alcohol_keywords.json")
    
    # TODO: Определять язык из конфига или аргументов
    lang = 'uk' 
    
    redistribute_products(other_file, keywords_file, lang)

if __name__ == "__main__":
    main()