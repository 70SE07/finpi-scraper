#!/usr/bin/env python3
"""
Скрипт для очистки товаров от артикулов и номеров
Удаляет все содержимое в скобках и лишние символы
"""
import os
import re
import glob
import logging

# Настройка логирования для автономного запуска
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def clean_product_name(product_name):
    """
    Очищает название товара от артикулов и лишних символов,
    корректно обрабатывая вложенные скобки.
    """
    cleaned = product_name
    # Повторяем замену, пока в строке остаются скобки
    while '(' in cleaned and ')' in cleaned:
        cleaned = re.sub(r'\([^()]*\)', '', cleaned)
    
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    return cleaned

def clean_file(file_path):
    """
    Очищает файл с товарами и возвращает результат.
    """
    if not os.path.exists(file_path):
        logging.error(f"Файл не найден: {os.path.basename(file_path)}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = [clean_product_name(line) for line in lines if line.strip()]
        cleaned_lines = [line for line in cleaned_lines if line] # Убираем пустые после очистки
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in cleaned_lines:
                f.write(line + '\n')
        
        # Логируем в одну строку для компактности
        logging.info(
            f"✅ Очищен файл: {os.path.basename(file_path)} "
            f"(Было: {len(lines)} -> Стало: {len(cleaned_lines)})"
        )
        return True
        
    except Exception as e:
        logging.error(f"Ошибка при обработке {os.path.basename(file_path)}: {e}")
        return False