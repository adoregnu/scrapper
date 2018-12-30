import os, re
import scrapy
import traceback
from .common import Common
from jav.items import JavItem

class Dmm(scrapy.Spider, Common):
    name = 'dmm'
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_dmm.PipelineDmm': 300 }
    }

    def start_requests(self):
        url = 'http://www.dmm.co.jp/en/search/=/searchstr='
        kws = self.prepare_request()
        for k in kws:
            yield scrapy.Request(url='%s%s/'%(url, self.get_cid(k)),
                callback=self.parse_search_list,
                cookies = self.cookies['www.dmm.co.jp']
            )

    def add_selector_ja(self, fields):
        fields.extend([
            ('releasedate', '//td[contains(., "商品発売日：")]/following-sibling::td[1]/text()'),
            ('runtime', '//td[contains(., "収録時間：")]/following-sibling::td[1]/text()'),
            ('director', '//td[contains(., "監督：")]/following-sibling::td[1]/a/text()'),
            ('set', '//td[contains(., "シリーズ：")]/following-sibling::td[1]/a/text()'),
            ('studio', '//td[contains(., "メーカー：")]/following-sibling::td[1]/a/text()'),
            ('label', '//td[contains(., "レーベル：")]/following-sibling::td[1]/a/text()'),
            ('genre', '//td[contains(., "ジャンル：")]/following-sibling::td[1]/a/text()')
        ])

    def add_selector_en(self, fields):
        fields.extend([
            ('releasedate', '//td[contains(., "Starting Date of Distribution:")]/following-sibling::td[1]/text()'),
            ('runtime', '//td[contains(., "Delivery time:")]/following-sibling::td[1]/text()'),
            ('director', '//td[contains(., "Supervision:")]/following-sibling::td[1]/a/text()'),
            ('set', '//td[contains(., "Series:")]/following-sibling::td[1]/a/text()'),
            ('studio', '//td[contains(., "Studios:")]/following-sibling::td[1]/a/text()'),
            ('label', '//td[contains(., "Label:")]/following-sibling::td[1]/a/text()'),
            ('genre', '//td[contains(., "Genre:")]/following-sibling::td[1]/a/text()')
        ])

    def parse_search_page(self, response):
        from scrapy.loader import ItemLoader
        lang = {'en' : self.add_selector_en, 'ja': self.add_selector_ja}
        fieldlist = [
            ('plot', 'div.mg-b20::text'),
            ('thumb', '#sample-video > div.tx10.pd-3 > a::attr(href)'),
            ('title', '//meta[@property="og:title"]/@content'),
            ('actor', '//*[@id="performer"]/a/text()')
        ]
        try :
            il = ItemLoader(item=JavItem(), response=response)
            lang[response.meta['lang']](fieldlist)
            self.initItemLoader(il, fieldlist)
            il.add_value('id', self.keyword)
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())

    def parse_search_list(self, response):
        results = response.css('p.tmb > a::attr(href)').extract()
        if not len(results):
            self.log('not found {}'.format(self.keyword))
            return

        self.log(results)

        prog = re.compile(r'cid=(\w+)/')
        cids = [prog.search(url).group(1) for url in results]
        if len(set(cids)) != 1:
            self.log('found more then 1 movies({}) from keyword:({})'.format(cids, self.keyword))
            return

        for ppm in [s for s in results if 'ppm/video' in s]:
            return scrapy.Request(url = ppm,
                callback = self.parse_search_page,
                cookies = self.cookies['www.dmm.co.jp'],
                meta = {'lang':'en'}
            )

        import copy
        for digital in [s for s in results if 'digital/videoa' in s]:
            cookie = copy.deepcopy(self.cookies['www.dmm.co.jp'])
            cookie[0]['value'] = 'ja'
            return scrapy.Request(url = digital,
                callback = self.parse_search_page,
                cookies = cookie,
                meta = {'lang':'ja'}
            )