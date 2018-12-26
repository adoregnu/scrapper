import os
import scrapy
import traceback
from .common import Common
from jav.items import JavItem

class Mgstage(scrapy.Spider, Common):
    name = 'mgstage'
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_mgs.PipelineMgs': 300 }
    }

    def start_requests(self):
        url = 'https://www.mgstage.com/product/product_detail/'
        kws = self.prepare_request()
        for k in kws:
            yield scrapy.Request(url='%s%s/'%(url, k), 
                callback = self.parse, 
                cookies = self.cookies['www.mgstage.com'])

    def parse(self, response):
        from scrapy.loader import ItemLoader
        try :
            #return self.parse_selector(response, selectors)
            il = ItemLoader(item=JavItem(), response=response)
            il.add_css('title', 'div.common_detail_cover > h1.tag::text')
            il.add_css('thumb', '#EnlargeImage::attr(href)')
            il.add_xpath('studio',  '//th[contains(., "メーカー：")]/following-sibling::td/a/@href')
            il.add_xpath('runtime', '//th[contains(., "収録時間：")]/following-sibling::td/text()')
            il.add_xpath('id',      '//th[contains(., "品番：")]/following-sibling::td/text()')
            il.add_xpath('date',    '//th[contains(., "配信開始日：")]/following-sibling::td/text()')
            il.add_xpath('rating',  '//th[contains(., "評価：")]/following-sibling::td//text()')
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())