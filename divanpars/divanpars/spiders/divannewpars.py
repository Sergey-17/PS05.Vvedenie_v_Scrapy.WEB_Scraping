import scrapy
from datetime import datetime


class DivannewparsSpider(scrapy.Spider):
    name = "divannewpars"
    allowed_domains = ["divan.ru", "www.divan.ru"]
    start_urls = ["https://www.divan.ru/blagoveshchensk/category/svet"]

    # Генерируем имя CSV файла: svet_YY-MM-DD_HH-MM.csv
    timestamp = datetime.now().strftime("%y-%m-%d_%H-%M")

    custom_settings = {
        "FEEDS": {
            f"svet_{timestamp}.csv": {
                "format": "csv",
                "encoding": "utf-8",
                "fields": ["name", "price", "url"],
            }
        },
        # Чуть ускорим, но бережно
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DOWNLOAD_DELAY": 0.5,
    }

    def parse(self, response):
        lamps = response.css('div.WdR1o')
        for lamp in lamps:
            name = lamp.css('div.lsooF span::text').get()
            price = lamp.css('div.pY3d2 span::text').get()
            href = lamp.css('a::attr(href)').get()
            absolute_url = response.urljoin(href) if href else None
            yield {
                "name": name,
                "price": price,
                "url": absolute_url,
            }

        # Пагинация: идём на следующую страницу, пока есть карточки
        if lamps:
            current_url = response.url.rstrip('/')
            current_page = 1
            if '/page-' in current_url:
                try:
                    current_page = int(current_url.rsplit('/page-', 1)[1])
                except ValueError:
                    current_page = 1
            next_page = current_page + 1
            base_without_page = current_url.split('/page-')[0]
            next_page_url = f"{base_without_page}/page-{next_page}"
            yield scrapy.Request(next_page_url, callback=self.parse)
