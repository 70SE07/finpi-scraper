#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Пакет утилит для FinPi Scraper
"""

__version__ = "1.0.0"
__author__ = "FinPi Team"

# Импорты для удобного использования
from .clean_products import clean_file
from .keyword_extractor import analyze_other_products, extract_keywords_from_products
from .keyword_analyzer import analyze_keywords_effectiveness, suggest_keyword_improvements

__all__ = [
    'clean_file', 
    'analyze_other_products',
    'extract_keywords_from_products',
    'analyze_keywords_effectiveness',
    'suggest_keyword_improvements'
]
