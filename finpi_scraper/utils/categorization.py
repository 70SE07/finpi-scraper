# finpi_scraper/utils/categorization.py
from .lemmatizer import lemmatize_text

def categorize_product(product_name: str, subcategory_keywords: dict, lang: str) -> str:
    """
    Определяет подкатегорию товара по ключевым словам с использованием лемматизации
    и с учетом негативных ключевых слов.
    
    Args:
        product_name (str): Название товара.
        subcategory_keywords (dict): Словарь с данными о подкатегориях.
        lang (str): Код языка ('en', 'de', 'uk', 'ru').

    Returns:
        str: Название подкатегории или 'other'.
    """
    if not subcategory_keywords:
        return 'other'
    
    product_lemmas = lemmatize_text(product_name, lang)
    product_lemmas_set = set(product_lemmas)

    for subcategory, data in subcategory_keywords.items():
        # Данные могут быть либо списком (старый формат), либо словарем
        positive_keywords = set(data if isinstance(data, list) else data.get('keywords', []))
        negative_keywords = set(data.get('negative_keywords', []) if isinstance(data, dict) else [])

        # 1. Проверяем наличие основного ключевого слова
        if not product_lemmas_set.isdisjoint(positive_keywords):
            # 2. Проверяем отсутствие негативных ключевых слов
            if product_lemmas_set.isdisjoint(negative_keywords):
                return subcategory  # Если совпадение есть и негативных слов нет
            else:
                # Найдено негативное слово, пропускаем эту категорию
                continue
            
    return 'other'
