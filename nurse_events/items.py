# -*- coding: utf-8 -*-

import scrapy

class EventItem(scrapy.Item):
    id_site = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()
    inserted = scrapy.Field()
