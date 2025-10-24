# finpi_scraper/scrapers/base_scraper.py
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    """
    Абстрактный базовый класс для всех скрейперов.
    Определяет общий интерфейс для парсинга сайтов.
    """
    def __init__(self, config):
        self.config = config
        self.site_name = config['site_name']
        self.base_url = config['url']
        self.selectors = config['product_name_selector']
        self.pagination_template = config.get('pagination_template', '')

    @abstractmethod
    def get_page_url(self, page: int) -> str:
        """
        Формирует URL для конкретной страницы пагинации.

        Args:
            page (int): Номер страницы.

        Returns:
            str: Полный URL страницы для парсинга.
        """
        pass

    def parse(self, html: str) -> list[str]:
        """
        Извлекает названия товаров из HTML-контента страницы.
        Использует селекторы, указанные в конфигурации.

        Args:
            html (str): HTML-контент страницы.

        Returns:
            list[str]: Список названий товаров.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        product_elements = []
        # Если селектор - это список, пробуем каждый по очереди
        if isinstance(self.selectors, list):
            for s in self.selectors:
                product_elements = soup.select(s)
                if product_elements:
                    # print(f"[{self.site_name}] Использован селектор: '{s}'") # Для отладки
                    break
        else:
            # Иначе работаем как обычно
            product_elements = soup.select(self.selectors)
        
        return [elem.get_text(strip=True) for elem in product_elements if elem.get_text(strip=True)]

