# -*- coding: utf-8 -*-

from scrapy.exceptions import DropItem, CloseSpider
from datetime import datetime
import logging
import pymongo

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class DuplicatesPipeline(object):

    # TODO Duplicado em DuplicatesPipeline e MongoPipeline
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
        logging.info('[DuplicatesPipeline] Opening connection with MongoDB')

    def close_spider(self, spider):
        # clean up when spider is closed
        self.client.close()
        logging.info('[DuplicatesPipeline] Closing connection with MongoDB')

    def process_item(self, item, spider):
        existent_event = self.db[self.collection_name].find_one({'title': item['title']})
        logging.debug(f"existing_event: {existent_event}")

        dup_check = self.db[self.collection_name].find({'title':item['title']}).count()
        logging.debug(f"dup_check: {dup_check}")
        # if dup_check == 0:

        if existent_event is not None: # the current event exists
            spider.close_down = True
            raise DropItem(f"Duplicate event found: {item['title']}")
        else:
            return item


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
        logging.info('[MongoPipeline] Opening connection with MongoDB')

    def close_spider(self, spider):
        # clean up when spider is closed
        self.client.close()
        logging.info('[MongoPipeline] Closing connection with MongoDB')

    def process_item(self, item, spider):
        item['inserted'] = datetime.now()
        self.db[self.collection_name].insert_one(dict(item))
        logging.debug(f"Nurse Event added to MongoDB: {item['title']}")
        return item
