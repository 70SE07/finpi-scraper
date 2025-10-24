# finpi_scraper/scrapers/rozetka_scraper.py
from .base_scraper import BaseScraper

class RozetkaScraper(BaseScraper):
    """
    Класс-парсер для сайта Rozetka.
    """
    def get_page_url(self, page: int) -> str:
        """
        Формирует URL для Rozetka.
        Пример: https://rozetka.com.ua/ua/krepkie-napitki/c4594292/page=2/
        """
        if page == 1:
            return self.base_url
        
        # pagination_template: "/page={page}/"
        return self.base_url.rstrip('/') + self.pagination_template.format(page=page)
