import re, os
import scrapy
import traceback

from .common import Common
from jav.items import JavItem

class SpiderAvwiki(scrapy.Spider, Common):
    name = 'avwiki'
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_avwiki.PipelineAvwiki': 300 }
    }

    def start_requests(self):
        url = 'https://shecool.net/av-wiki/?s='
        for id in self.cids:
            yield scrapy.Request(
                url = '%s%s' % (url, id['cid'].upper()),
                callback=self.parse_search_result,
                meta={'id':id}
            )

    def parse_search_result(self, response):
        result = response.css('div.archive-title > h1 > span::text').extract()
        if len(result) != 2:
            self.log('unkown result!')
            #self.save_html(response.body, 'avwiki-search')
            return
        if int(result[1][0]) != 1:
            self.log(('not found!! {}').format(result[1]))
            return
        href = response.css('h2.archive-header-title > a::attr(href)').extract_first()
        yield scrapy.Request(url=href, callback=self.parse_real_result, meta=response.meta)

    def parse_real_result(self, response):
        selectors = [
            'div.contents-box:contains("{}")',
            'div.col6 > p:contains("{}")',
        ]
        links = None
        id = response.meta['id']
        for css in selectors:
            content = response.css(css.format(id['cid'].upper()))
            if len(content) > 0:
                links = content.css('a::attr(href)').extract()
                break
        self.log(links)
        if not links:
            self.log('could not parse html!')
            #self.save_html(response.body, 'avwiki-real')
            return

        sites = {
            'www.mgstage.com':self.parse_movie_info, 
            'www.dmm.co.jp':self.parse_dmm_cid_list
        }
        links = set(links)
        item = JavItem()
        for link in list(links):
            domain = link.split('/')[2]
            if not sites.get(domain):
                self.log('unknown domain! %s' % domain)
                continue

            if domain == 'www.mgstage.com':
                link = 'https://www.mgstage.com/product/product_detail/%s'%link.split('/')[-2]

            yield scrapy.Request(
                url = link,
                callback = sites[domain],
                cookies = self.cookies[domain],
                meta = {'item':item, 'id':id}
            )

    def parse_movie_info(self, response):
        from scrapy.loader import ItemLoader
        try:
            il = ItemLoader(item=response.meta['item'], response=response)
            il.add_css('title', 'div.common_detail_cover > h1.tag::text')
            il.add_css('thumb', '#EnlargeImage::attr(href)')
            il.add_xpath('studio',  '//th[contains(., "メーカー：")]/following-sibling::td/a/@href')
            il.add_xpath('runtime', '//th[contains(., "収録時間：")]/following-sibling::td/text()')
            il.add_xpath('id', '//th[contains(., "品番：")]/following-sibling::td/text()')
            il.add_xpath('releasedate', '//th[contains(., "配信開始日：")]/following-sibling::td/text()')
            il.add_xpath('rating',  '//th[contains(., "評価：")]/following-sibling::td//text()')
            return il.load_item()
        except:
            #self.save_html(response.body)
            self.log(traceback.format_exc())