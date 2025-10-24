#!/usr/bin/env python3
"""
Скрипт для очистки товаров от артикулов и номеров
Удаляет все содержимое в скобках и лишние символы
"""
import os
import re
import glob

def clean_product_name(product_name):
    """
    Очищает название товара от артикулов и лишних символов
    """
    # Удаляем все содержимое в скобках
    cleaned = re.sub(r'\([^)]*\)', '', product_name)
    
    # Удаляем множественные пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Удаляем пробелы в начале и конце
    cleaned = cleaned.strip()
    
    return cleaned

def clean_file(file_path):
    """
    Очищает файл с товарами
    """
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return False
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Очищаем каждую строку
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Пропускаем пустые строки
                cleaned_line = clean_product_name(line)
                if cleaned_line:  # Добавляем только непустые строки
                    cleaned_lines.append(cleaned_line)
        
        # Записываем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in cleaned_lines:
                f.write(line + '\n')
        
        print(f"✅ Очищен файл: {file_path}")
        print(f"   Было строк: {len(lines)}")
        print(f"   Стало строк: {len(cleaned_lines)}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")
        return False

def main():
    """
    Основная функция для очистки всех файлов с товарами
    """
    print("🧹 НАЧИНАЮ ОЧИСТКУ ТОВАРОВ ОТ АРТИКУЛОВ")
    print("=" * 50)
    
    # Ищем все файлы с товарами
    output_dir = "output"
    pattern = os.path.join(output_dir, "**", "*.txt")
    files = glob.glob(pattern, recursive=True)
    
    if not files:
        print("❌ Файлы с товарами не найдены")
        return
    
    print(f"📁 Найдено файлов: {len(files)}")
    
    success_count = 0
    for file_path in files:
        print(f"\n📄 Обрабатываю: {file_path}")
        if clean_file(file_path):
            success_count += 1
    
    print(f"\n🎉 ОЧИСТКА ЗАВЕРШЕНА!")
    print(f"✅ Успешно обработано: {success_count} файлов")
    print(f"❌ Ошибок: {len(files) - success_count} файлов")

if __name__ == "__main__":
    main()
