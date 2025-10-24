#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилита для извлечения ключевых слов, словосочетаний и предложений стоп-слов.
"""

import json
import os
from collections import Counter
from datetime import datetime
import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from .lemmatizer import lemmatize_text

# --- Глобальные переменные и настройки ---
_stopwords = {}
LANG_MAP = {"uk": "ukrainian", "ru": "russian", "en": "english"}
STOPWORD_SUGGESTION_THRESHOLD = 0.1 # Считать слово кандидатом в стоп-слова, если оно встречается более чем в 10% товаров

def _load_stopwords():
    """Загружает кастомные и стандартные стоп-слова."""
    global _stopwords
    stopwords_path = os.path.join(os.path.dirname(__file__), '..', 'keywords', 'stopwords.json')
    custom_stopwords = {}
    if os.path.exists(stopwords_path):
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            custom_stopwords = json.load(f)

    for lang_code, lang_name in LANG_MAP.items():
        try:
            nltk_stopwords = set(nltk.corpus.stopwords.words(lang_name))
            custom = set(custom_stopwords.get(lang_code, []))
            _stopwords[lang_code] = nltk_stopwords.union(custom)
        except (OSError, KeyError):
            print(f"Предупреждение: не удалось загрузить стоп-слова для языка '{lang_name}'.")
            _stopwords[lang_code] = set(custom_stopwords.get(lang_code, []))

_load_stopwords()

def extract_keywords_from_products(products, lang, min_freq=2):
    """
    Извлекает ключевые слова, фразы и кандидатов в стоп-слова.
    Возвращает (potential_keywords, stopword_candidates)
    """
    print(f"🔍 Анализирую {len(products)} товаров (язык: {lang})...")
    
    all_lemmas = []
    for product in products:
        lemmas = lemmatize_text(product, lang)
        filtered = [lemma for lemma in lemmas if lemma not in _stopwords.get(lang, set()) and len(lemma) > 2]
        all_lemmas.extend(filtered)

    unigram_freq = Counter(all_lemmas)
    
    finder = BigramCollocationFinder.from_words(all_lemmas)
    finder.apply_freq_filter(min_freq)
    bigram_measures = BigramAssocMeasures()
    found_bigrams = finder.nbest(bigram_measures.pmi, 50)

    potential_keywords = {}
    stopword_candidates = []

    # Обработка биграмм - это всегда ключевые фразы
    for bg in found_bigrams:
        phrase = " ".join(bg)
        potential_keywords[phrase] = finder.ngram_fd[bg]

    # Обработка униграмм - могут быть и ключами, и стоп-словами
    stopword_freq_threshold = len(products) * STOPWORD_SUGGESTION_THRESHOLD
    for word, count in unigram_freq.items():
        if count >= min_freq:
            # Если слово встречается СЛИШКОМ часто, это кандидат в стоп-слова
            if count > stopword_freq_threshold and len(products) > 10: # Порог для больших выборок
                stopword_candidates.append(word)
            else:
                potential_keywords[word] = count

    sorted_keywords = dict(sorted(potential_keywords.items(), key=lambda item: item[1], reverse=True))
    
    print(f"📊 Найдено {len(sorted_keywords)} потенциальных ключей и {len(stopword_candidates)} кандидатов в стоп-слова.")
    print(f"🔝 Топ-10 ключей: {list(sorted_keywords.items())[:10]}")
    if stopword_candidates:
        print(f"💡 Кандидаты в стоп-слова: {stopword_candidates}")
    
    return sorted_keywords, stopword_candidates

def analyze_other_products(other_file_path, lang='uk'):
    """
    Анализирует товары из файла OTHER. Возвращает (ключи, кандидаты в стоп-слова).
    """
    if not os.path.exists(other_file_path):
        print(f"❌ Файл {other_file_path} не найден")
        return None, None
    
    with open(other_file_path, 'r', encoding='utf-8') as f:
        products = [line.strip() for line in f.readlines() if line.strip()]
    
    if not products:
        print("📁 Файл OTHER пуст")
        return None, None
    
    print(f"📁 Найдено {len(products)} товаров в файле OTHER")
    
    return extract_keywords_from_products(products, lang)

def update_suggested_stopwords(stopwords_file, suggestions):
    """
    Добавляет новые предложенные стоп-слова в `suggested_stopwords.json`.
    """
    if not suggestions:
        return

    if os.path.exists(stopwords_file):
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            try:
                existing = set(json.load(f))
            except json.JSONDecodeError:
                existing = set()
    else:
        existing = set()
        
    new_suggestions = [s for s in suggestions if s not in existing]

    if new_suggestions:
        updated_list = sorted(list(existing.union(new_suggestions)))
        with open(stopwords_file, 'w', encoding='utf-8') as f:
            json.dump(updated_list, f, ensure_ascii=False, indent=2)
        print(f"✍️ В `suggested_stopwords.json` добавлено {len(new_suggestions)} новых кандидатов: {new_suggestions}")

def main():
    """
    Основная функция для анализа товаров из OTHER.
    """
    print("🔍 АНАЛИЗ ТОВАРОВ ИЗ КАТЕГОРИИ OTHER")
    print("="*50)
    
    other_file = "output/GOODS/GROCERIES/BEVERAGES/rozetka_alcohol_other.txt"
    keywords_file = "keywords/alcohol_keywords.json"
    suggested_stopwords_file = "keywords/suggested_stopwords.json"
    
    keywords, stopwords = analyze_other_products(other_file, lang='uk')
    
    if keywords:
        update_keywords_file(keywords_file, keywords, "other_analysis")
    if stopwords:
        update_suggested_stopwords(suggested_stopwords_file, stopwords)
    
    print("\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()
