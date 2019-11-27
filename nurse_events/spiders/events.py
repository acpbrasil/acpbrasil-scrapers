# -*- coding: utf-8 -*-
import scrapy
from nurse_events.items import EventItem
from scrapy.exceptions import CloseSpider
import logging

class EventsSpider(scrapy.Spider):
    name = 'events'
    allowed_domains = ['portaldaenfermagem.com.br']
    start_urls = ['https://www.portaldaenfermagem.com.br/agenda-de-eventos']
    
    close_down = False

    def parse(self, response):
        # for row in response.xpath('//table//tr[position()>1]'):
        # for row in response.xpath('//table//tr[position() > 1 and position() < last()]'):
        for row in response.xpath('//table//tr[position() = 2]'): # FIXME

            if self.close_down:
                logging.warn('Closing spider: All new events were processed - no need to go further')
                raise CloseSpider('Closing spider: All new events were processed - no need to go further')

            item = EventItem()
            item['title'] = row.xpath('td[1]//text()').extract_first()
            item['date'] = row.xpath('td[2]//text()').extract_first()
            item['location'] = row.xpath('td[3]//text()').extract_first()
            yield item
