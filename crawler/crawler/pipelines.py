# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import Engine


class DropEmptyItems:
    def process_item(self, item, spider):
        prep_item = ItemAdapter(item)

        for field in ["date", "header", "url", "content"]:
            if len(str(prep_item.get(field))) == 0:
                raise DropItem(f"item has empty field \"{field}\"")

        return item

class InsertIntoDatabase:
    def process_item(self, item, spider):
        prep_item = ItemAdapter(item)

        for field in ["date", "header", "url", "content"]:
            if len(str(prep_item.get(field))) == 0:
                raise DropItem(f"item has empty field \"{field}\"")

        return item
