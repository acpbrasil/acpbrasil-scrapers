# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem, CloseSpider
from datetime import datetime
import logging
import pymongo
import requests

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class ValidatePipeline(object):
    def process_item(self, item, spider):
        if item['title'] and item['date']:
            return item
        else:
            raise DropItem(f"Missing data: {item}")


# XXX Should separate the duplicate logic in a different Pipeline?
# class DuplicatesPipeline(object):
#     def process_item(self, item, spider):
#         return item

class MongoPipeline(object):

    collection_name = 'events'
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        # pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB', 'items')
        )

    def open_spider(self, spider):
        # initializing spider - opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # self.db.authenticate(self.mongo_user, self.mongo_passw)
        logging.info('[MongoPipeline] Opening connection with MongoDB')

    def close_spider(self, spider):
        # clean up when spider is closed
        self.client.close()
        logging.info('[MongoPipeline] Closing connection with MongoDB')

    def process_item(self, item, spider):
        if self.is_duplicate(item):
            # spider.close_down = True
            # spider.crawler.engine.close_spider(self, reason='All new events processed')
            raise DropItem(f"Duplicate event found: {item['title']}")
        else:
            item['inserted'] = datetime.now()
            self.db[self.collection_name].insert_one(dict(item))
            logging.debug(f"Nurse Event added to MongoDB: \"{item['title']}\"")
            return item
            
    def is_duplicate(self, item):
        existent_event = self.db[self.collection_name].find_one({'id_site': item['id_site']})
        return existent_event is not None
        # dup_check = self.db[self.collection_name].find({'id_site':item['id_site']}).count()
        # return dup_check > 0


class NotifyTelegramPipeline(object):

    def __init__(self, bot_api_key, channel_name):
        self.bot_api_key = bot_api_key
        self.channel_name = channel_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            bot_api_key=crawler.settings.get('TELEGRAM_BOT_API_KEY'),
            channel_name=crawler.settings.get('TELEGRAM_CHANNEL_NAME')
        )

    def process_item(self, item, spider):
        logging.debug(f"Sending new event \"{item['title']}\" to Telegram...")
        msg_text = (
            "*Novo evento de enfermagem:*\n\n"
            f"{item['title']}\n"
            f"Data: {item['date']}\n"
            f"Onde: {item['location']}"
        )

        requests.get(
            f"https://api.telegram.org/bot{self.bot_api_key}/sendMessage",
            params = {
                'chat_id': self.channel_name,
                'parse_mode': 'Markdown',
                'text': msg_text
            })
        return item
