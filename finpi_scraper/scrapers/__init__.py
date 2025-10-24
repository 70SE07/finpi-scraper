# finpi_scraper/scrapers/__init__.py

from .rozetka_scraper import RozetkaScraper
from .tesco_scraper import TescoScraper
from .rost_scraper import RostScraper

# Словарь-фабрика для выбора нужного класса скрейпера
SCRAPER_CLASSES = {
    'rozetka': RozetkaScraper,
    'tesco': TescoScraper,
    'rost': RostScraper,
}

def get_scraper(config):
    """
    Фабричная функция для получения экземпляра нужного скрейпера.
    """
    site_name = config.get('site_name')
    scraper_class = SCRAPER_CLASSES.get(site_name)
    
    if scraper_class:
        return scraper_class(config)
    else:
        raise ValueError(f"Не найден скрейпер для сайта: {site_name}")