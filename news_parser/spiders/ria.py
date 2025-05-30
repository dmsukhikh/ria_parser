import scrapy


class RiaSpider(scrapy.Spider):
    name = "ria"
    allowed_domains = ["ria.ru"]
    start_urls = ["https://ria.ru"]

    def parse(self, response):
        pass
