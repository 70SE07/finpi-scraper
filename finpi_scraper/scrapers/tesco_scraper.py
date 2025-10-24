# finpi_scraper/scrapers/tesco_scraper.py
from .base_scraper import BaseScraper

class TescoScraper(BaseScraper):
    """
    Класс-парсер для сайта Tesco.
    """
    def get_page_url(self, page: int) -> str:
        """
        Формирует URL для Tesco.
        Пример: https://www.tesco.com/groceries/en-GB/shop/drinks/spirits/all?page=2
        """
        if page == 1:
            return self.base_url
        
        # pagination_template: "?page={page}"
        if '?' in self.base_url:
            return self.base_url + '&' + self.pagination_template.format(page=page).lstrip('?')
        else:
            return self.base_url + self.pagination_template.format(page=page)
