# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine, URL
import sqlalchemy
import logging

from sqlalchemy.exc import DBAPIError


class DropEmptyItems:
    def process_item(self, item, spider):
        prep_item = ItemAdapter(item)

        for field in ["date", "header", "url", "content"]:
            if len(str(prep_item.get(field))) == 0:
                raise DropItem(f"item has empty field \"{field}\"")

        return item

class HandleDate:
    def process_item(self, item, spider):
        prep_item = ItemAdapter(item)
        
        date = prep_item["date"]
        date = date.split()[::-1]
        day = date[0].split('.')
        date = '-'.join(day[::-1]) + " " + date[1]



        prep_item.update({"date": date})
        return item

class InsertIntoDatabase:
    def __init__(self, user, passwd, host, port, db):
        self.db_url = URL.create(
            "postgresql",
            username=user,
            password=passwd,
            host=host,
            port=port,
            database=db
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user = crawler.settings.get("POSTGRES_USERNAME"),
            passwd = crawler.settings.get("POSTGRES_PASSWORD"),
            host = crawler.settings.get("POSTGRES_HOST"),
            port = crawler.settings.get("POSTGRES_PORT"),
            db = crawler.settings.get("POSTGRES_DATABASE")
        )

    def open_spider(self, spider):
        self.engine = create_engine(self.db_url)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        with self.engine.connect() as connection:
            # inserting data into articles
            try:
                t = sqlalchemy.text("INSERT INTO articles VALUES ( "
                                    "DEFAULT, :header, :url, "
                                    ":date, :content) ")
                connection.execute(t, {"header": adapter.get("header"),
                                       "url": adapter.get("url"),
                                       "date": adapter.get("date"),
                                       "content": adapter.get("content")}
                                   )
            except DBAPIError:
                logging.log(
                    logging.INFO, 
                    f"Dublicating while inserting item {adapter.get("url")}")
                connection.rollback()
                raise DropItem("Dublicate")

            # save the article
            # fetching id of the tuple
            id = connection.execute(
                    sqlalchemy.text(f"SELECT id FROM articles WHERE "
                                    f"url='{item.get("url")}'")
                    ).first()
            if id is not None:
                id = id[0]

            #inserting tags and entries into many-to-many table
            for tag in adapter.get("tags", []):
                with connection.begin_nested() as sp:
                    try:
                        connection.execute(sqlalchemy.text(
                            f"INSERT INTO tags VALUES (DEFAULT, '{tag}')"))
                    except DBAPIError:
                        logging.log(
                            logging.INFO, f"Dublicating while inserting tag {tag}")
                        sp.rollback()

                # fetching id of the tag tuple
                tag_id = connection.execute(
                        sqlalchemy.text(f"SELECT id FROM tags WHERE "
                                        f"name='{tag}'")
                        ).first()
                if tag_id is not None:
                    tag_id = tag_id[0]


                with connection.begin_nested() as sp:
                    try:
                        connection.execute(sqlalchemy.text(
                            f"INSERT INTO tags_of_articles VALUES ( "
                            f"DEFAULT, '{id}', '{tag_id}')"))
                    except DBAPIError:
                        logging.log(
                            logging.INFO, f"Dublicating while inserting tag {tag}")
                        sp.rollback()

            connection.commit() 

