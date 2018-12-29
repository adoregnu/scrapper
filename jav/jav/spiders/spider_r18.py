import os, re
import scrapy
import traceback
from .common import Common

class SpiderR18(scrapy.Spider, Common):
    name = 'r18'
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_r18.PipelineR18': 300 }
    }

    def start_requests(self):
        url = 'http://www.r18.com/common/search/searchword='
        kws = self.prepare_request()
        for k in kws:
            yield scrapy.Request(url='%s%s/'%(url, self.get_cid(k)),
                callback=self.parse_search_list,
                cookies = self.cookies['www.r18.com']
            )

    def parse_search_page(self, response):
        from scrapy.loader import ItemLoader
        from jav.items import JavItem
        try :
            il = ItemLoader(item=JavItem(), response=response)
            il.add_xpath('title',    '//meta[@property="og:title"]/@content')
            il.add_xpath('date',     '//dt[contains(.,"Release Date:")]/following-sibling::dd[1]/text()')
            il.add_xpath('runtime',  '//dt[contains(.,"Runtime:")]/following-sibling::dd[1]/text()')
            il.add_xpath('director', '//dt[contains(.,"Director:")]/following-sibling::dd[1]/text()')
            il.add_xpath('set',      '//dt[contains(.,"Series:")]/following-sibling::dd[1]/a')
            il.add_xpath('studio',   '//dt[contains(.,"Studio:")]/following-sibling::dd[1]/a/text()')
            il.add_xpath('label',    '//dt[contains(.,"Label:")]/following-sibling::dd[1]/text()')
            il.add_xpath('actor',    '//label[contains(.,"Actress(es):")]/following-sibling::div[1]/span/a/span/text()')
            il.add_xpath('genre',    '//label[contains(.,"Categories:")]/following-sibling::div[1]/a/text()')
            il.add_xpath('plot',     '//h1[contains(., "Product Description")]/following-sibling::p/text()')
            il.add_css('thumb',      'div.box01.mb10.detail-view > img::attr(src)')
            il.add_css('actor_thumb','ul.cmn-list-product03.clearfix.mr07 > li > a > p > img::attr(src)')
            il.add_value('id', self.keyword)
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())

    def parse_search_list(self, response):
        results = response.css('ul.cmn-list-product01.type01 > li > a::attr(href)').extract()

        prog = re.compile(r'id=(?:h_)?(?:\d+)?([a-z0-9]+[0-9]{5})/')
        cids = list(filter(lambda x: prog.search(x).group(1) == self.get_cid().lower(), results))
        self.log(cids)
        if len(set(cids)) != 1:
            self.log('no exact matched with keyword:({})'.format(self.get_cid().lower()))
            self.log('found urls {}'.format(results))
            return

        for url in cids:
            self.log(url)
            return scrapy.Request(url=url,
                callback = self.parse_search_page,
                cookies = self.cookies['www.r18.com']
            )