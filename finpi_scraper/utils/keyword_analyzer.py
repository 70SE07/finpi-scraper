#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилита для анализа и обновления ключевых слов
"""

import json
import os
from datetime import datetime

def load_keywords(keywords_file):
    """
    Загружает ключевые слова из файла.
    """
    if not os.path.exists(keywords_file):
        print(f"❌ Файл {keywords_file} не найден")
        return {}
    
    with open(keywords_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_keywords(keywords_file, data):
    """
    Сохраняет ключевые слова в файл.
    """
    with open(keywords_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def merge_keywords(existing_keywords, new_keywords, category_name):
    """
    Объединяет существующие и новые ключевые слова.
    """
    if category_name not in existing_keywords:
        existing_keywords[category_name] = {
            'keywords': [],
            'confidence': 0.5,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    # Объединяем ключевые слова
    existing_set = set(existing_keywords[category_name]['keywords'])
    new_set = set(new_keywords.keys())
    
    # Добавляем только новые ключевые слова
    new_keywords_list = list(new_set - existing_set)
    
    if new_keywords_list:
        existing_keywords[category_name]['keywords'].extend(new_keywords_list)
        existing_keywords[category_name]['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Повышаем уверенность при добавлении новых ключевых слов
        existing_keywords[category_name]['confidence'] = min(
            existing_keywords[category_name]['confidence'] + 0.1, 1.0
        )
        
        print(f"✅ Добавлено {len(new_keywords_list)} новых ключевых слов для '{category_name}'")
        print(f"🔤 Новые ключевые слова: {new_keywords_list}")
    else:
        print(f"ℹ️ Новых ключевых слов для '{category_name}' не найдено")

def analyze_keywords_effectiveness(keywords_file, other_file):
    """
    Анализирует эффективность ключевых слов.
    """
    print("📊 АНАЛИЗ ЭФФЕКТИВНОСТИ КЛЮЧЕВЫХ СЛОВ")
    print("="*50)
    
    # Загружаем ключевые слова
    keywords_data = load_keywords(keywords_file)
    
    if not keywords_data:
        print("❌ Ключевые слова не найдены")
        return
    
    # Читаем товары из OTHER
    if not os.path.exists(other_file):
        print(f"❌ Файл {other_file} не найден")
        return
    
    with open(other_file, 'r', encoding='utf-8') as f:
        other_products = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"📁 Анализирую {len(other_products)} товаров из OTHER")
    
    # Анализируем каждую категорию
    for category, data in keywords_data.items():
        if category == 'other_analysis':
            continue
            
        keywords = data['keywords']
        matched_products = []
        
        for product in other_products:
            product_lower = product.lower()
            for keyword in keywords:
                if keyword.lower() in product_lower:
                    matched_products.append(product)
                    break
        
        if matched_products:
            print(f"\n🎯 {category.upper()}:")
            print(f"   📊 Найдено совпадений: {len(matched_products)}")
            print(f"   🔤 Ключевые слова: {keywords[:5]}...")  # Показываем первые 5
            print(f"   📝 Примеры товаров: {matched_products[:3]}")  # Показываем первые 3
    
    print(f"\n📈 Общая статистика:")
    print(f"   📁 Всего товаров в OTHER: {len(other_products)}")
    print(f"   🏷️ Всего категорий: {len(keywords_data)}")

def suggest_keyword_improvements(keywords_file):
    """
    Предлагает улучшения для ключевых слов.
    """
    print("\n💡 ПРЕДЛОЖЕНИЯ ПО УЛУЧШЕНИЮ КЛЮЧЕВЫХ СЛОВ")
    print("="*50)
    
    keywords_data = load_keywords(keywords_file)
    
    for category, data in keywords_data.items():
        if category == 'other_analysis':
            continue
            
        keywords = data['keywords']
        confidence = data['confidence']
        
        print(f"\n🏷️ {category.upper()}:")
        print(f"   📊 Уверенность: {confidence:.2f}")
        print(f"   🔤 Количество ключевых слов: {len(keywords)}")
        
        if confidence < 0.7:
            print(f"   ⚠️ Низкая уверенность - рекомендуется добавить больше ключевых слов")
        
        if len(keywords) < 5:
            print(f"   ⚠️ Мало ключевых слов - рекомендуется расширить список")
        
        # Предлагаем синонимы
        if 'whisky' in category.lower():
            print(f"   💡 Рекомендации: добавить 'скотч', 'бурбон', 'теннесси'")
        elif 'vodka' in category.lower():
            print(f"   💡 Рекомендации: добавить 'водочка', 'первак', 'хортиця'")

def main():
    """
    Основная функция для анализа ключевых слов.
    """
    keywords_file = "keywords/alcohol_keywords.json"
    other_file = "output/GOODS/GROCERIES/BEVERAGES/rozetka_alcohol_other.txt"
    
    # Анализируем эффективность
    analyze_keywords_effectiveness(keywords_file, other_file)
    
    # Предлагаем улучшения
    suggest_keyword_improvements(keywords_file)

if __name__ == "__main__":
    main()
