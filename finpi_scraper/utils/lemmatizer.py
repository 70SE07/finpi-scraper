# finpi_scraper/utils/lemmatizer.py
import spacy
import logging

# Загружаем модели один раз при старте, чтобы избежать повторной загрузки
# Это может занять несколько секунд при первом импорте модуля
NLP_MODELS = {}
MODEL_NAMES = {
    "en": "en_core_web_sm",
    "de": "de_core_news_sm",
    "uk": "uk_core_news_sm",
    "ru": "ru_core_news_sm",
}

for lang, model_name in MODEL_NAMES.items():
    try:
        NLP_MODELS[lang] = spacy.load(model_name)
        logging.info(f"Загружена NLP модель для языка: '{lang}'")
    except OSError:
        logging.error(
            f"Не удалось загрузить модель spaCy '{model_name}'. "
            f"Пожалуйста, скачайте ее командой: python -m spacy download {model_name}"
        )

def lemmatize_text(text: str, lang: str) -> list[str]:
    """
    Приводит все слова в тексте к их базовой форме (лемме) для указанного языка.

    Args:
        text (str): Входной текст (например, название товара).
        lang (str): Код языка ('en', 'de', 'uk', 'ru').

    Returns:
        list[str]: Список лемм (базовых форм слов).
    """
    if lang not in NLP_MODELS:
        logging.warning(f"Модель для языка '{lang}' не найдена. Лемматизация пропущена.")
        # Возвращаем просто слова в нижнем регистре, если нет модели
        return text.lower().split()

    doc = NLP_MODELS[lang](text)
    
    # Возвращаем лемму для каждого токена, если это слово или число
    lemmas = [
        token.lemma_.lower() 
        for token in doc 
        if token.is_alpha or token.is_digit
    ]
    
    return lemmas

def lemmatize_keywords(keywords: list[str], lang: str) -> list[str]:
    """
    Приводит список ключевых слов к их базовой форме (лемме).
    """
    # Объединяем в один текст для более эффективной обработки spaCy
    text = " ".join(keywords)
    return lemmatize_text(text, lang)
