# finpi_scraper/scrapers/rost_scraper.py
from .base_scraper import BaseScraper

class RostScraper(BaseScraper):
    """
    Класс-парсер для сайта Rost.
    """
    def get_page_url(self, page: int) -> str:
        """
        Формирует URL для Rost.
        Пример: https://rostmarket.com.ua/alkogol/?p=2
        """
        if page == 1:
            return self.base_url
        
        # pagination_template: "?p={page}"
        if '?' in self.base_url:
            return self.base_url + '&' + self.pagination_template.format(page=page).lstrip('?')
        else:
            return self.base_url + self.pagination_template.format(page=page)
