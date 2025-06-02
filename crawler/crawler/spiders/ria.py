from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import texttable


class RiaSpider(CrawlSpider):
    name = "ria"
    allowed_domains = ["ria.ru"]
    start_urls = ["https://ria.ru"] 
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "DEPTH_LIMIT": 4,
        "DOWNLOAD_DELAY": 1.5,
        "ROBOTSTXT_OBEY": True,
        "CLOSESPIDER_ITEMCOUNT": 200
    }

    rules = (
        Rule(link_extractor=LinkExtractor(
            allow_domains="ria.ru", allow=r"\/\d+\/.+html"), callback="parse_item", follow=True),
    )

    def _get_plain_text(self, html_text : str) -> str:
        return re.sub("<[^<>]*>", "", html_text)

    def _parse_content(self, response) -> str:
       parsed_article_text = ""

       for block in response.css("div[class=article__block]"):
           if "data-type" not in block.attrib:
               continue

           if block.attrib["data-type"] == "text":
               parsed_article_text += self._get_plain_text(
                   block.css("div[class=article__text]").get())

           elif block.attrib["data-type"] == "list":
               for item in block.css("li[class=article__list-item]::text"):
                   parsed_article_text += "\t- " + item.get() + "\n"
               continue

           elif block.attrib["data-type"] == "table":
               table = texttable.Texttable(max_width=0)
               row = [txt for txt in block.css("p::text")]
               if len(row) == 0:
                   row = ["" for _ in block.css("td")]
               table.add_row(row)
               parsed_article_text += str(table.draw())

           elif re.match("^h\\d$", block.attrib["data-type"]):
               parsed_article_text += "\n" + \
                   block.css(
                       block.attrib["data-type"]+"::text").get() + "\n"
           else:
               continue

           parsed_article_text += "\n"
       return parsed_article_text

    def _parse_tags(self, response) -> list[str]:
        return [tag for tag 
                in response.css("a[class=article__tags-item]::text").getall()]


    def parse_item(self, response):
        date = response.css(
            "div[class=article__info-date]").css("a::text").get()
        
        header = response.css("div[class=article__title]::text").get()
        if header is None:
            header = response.css("h1[class=article__title]::text").get()

        content = self._parse_content(response)
        tags = self._parse_tags(response)

        return {"date": date, "header": header, 
                "url": re.sub("\\?.*$", "", response.url), 
                "content": content, "tags": tags}
