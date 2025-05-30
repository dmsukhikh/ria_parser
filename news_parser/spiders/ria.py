import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class RiaSpider(CrawlSpider):
    name = "ria"
    allowed_domains = ["ria.ru"]
    # start_urls = ["https://ria.ru"] 
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "DEPTH_LIMIT": 10,
        "DOWNLOAD_DELAY": 1.5,
        "ROBOTSTXT_OBEY": True
    }

    rules = (
        Rule(link_extractor=LinkExtractor(
            allow_domains="ria.ru", allow="\\.html$")),
    )

    def parse(self, response):
        parsed_article_text = ""

        for block in response.css("div[class=article__block]"):
            if ("data-type" not in block.attrib):
                continue

            if (block.attrib["data-type"] == "text"):
                for part in block.css("div[class=article__text]"):
                    parsed_article_text += part.css("*::text").get()

        yield {"content": parsed_article_text}

