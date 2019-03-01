import os
import scrapy
import traceback
from .common import Common 
from jav.items import JavItem

class JavBus(scrapy.Spider, Common):
    name = "javbus"
    #custom_settings = {
    #    'ITEM_PIPELINES': { 'jav.pipelines.pipe_javlib.PipelineJavlib': 300 }
    #}

    def start_requests(self):
        url = 'https://www.javbus.com/ja/uncensored/search/%s&type=1'
        kws = self.prepare_request()
        for k in kws:
            yield scrapy.Request(url=url % k, callback=self.parse_search)

    def parse_search(self, response):
        self.save_html(response.body)

    def parse(self, response):
        from scrapy.loader import ItemLoader
        try:
            il = ItemLoader(item=JavItem(), response=response)
            il.add_xpath('title', '//*[@id="video_title"]/h3/a/text()')
            il.add_xpath('id', '//*[@id="video_id"]/table/tr/td[2]/text()')
            il.add_xpath('releasedate', '//*[@id="video_date"]/table/tr/td[2]/text()')
            il.add_xpath('director', '//*[@id="video_director"]/table/tr/td[2]/span/a/text()')
            il.add_xpath('studio', '//*[@id="video_maker"]/table/tr/td[2]/span/a/text()')
            il.add_xpath('thumb', '//*[@id="video_jacket_img"]/@src')
            il.add_xpath('rating', '//*[@id="video_review"]/table/tr/td[2]/span[1]/text()')
            il.add_xpath('genre', '//*[@id="video_genres"]/table/tr/td[2]/span/a//text()')
            il.add_xpath('actor', '//*[@id="video_cast"]/table/tr/td[2]')
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())