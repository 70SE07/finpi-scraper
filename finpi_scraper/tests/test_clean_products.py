# finpi_scraper/tests/test_clean_products.py
import pytest
import sys
import os

# Добавляем путь к родительской директории, чтобы можно было импортировать utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.clean_products import clean_product_name

# Используем параметризацию pytest для проверки нескольких случаев
@pytest.mark.parametrize("input_name, expected_name", [
    ("Виски (Whisky) Johnnie Walker Red Label 0.7л", "Виски Johnnie Walker Red Label 0.7л"),
    ("Вино  (красное, сухое)   1л", "Вино 1л"),
    ("Товар без скобок", "Товар без скобок"),
    ("  Лишние пробелы в начале и конце  ", "Лишние пробелы в начале и конце"),
    ("Товар (с вложенными (скобками))", "Товар"), # Тест на вложенные скобки (не идеально, но проверяем текущее поведение)
    ("Товар(без пробела)", "Товар"),
    ("", ""), # Пустая строка
    ("   ", ""), # Строка из пробелов
])
def test_clean_product_name(input_name, expected_name):
    """
    Тестирует функцию clean_product_name на различных входных данных.
    """
    assert clean_product_name(input_name) == expected_name
