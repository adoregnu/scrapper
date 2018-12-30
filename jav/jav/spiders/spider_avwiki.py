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
        kws = self.prepare_request()
        for kw in kws:
            yield scrapy.Request(
                url = '%s%s' % (url, kw.upper()),
                callback=self.parse_search_result
            )

    def parse_search_result(self, response):
        result = response.css('div.archive-title > h1 > span::text').extract()
        if len(result) != 2:
            self.log('unkown result!')
            self.save_html(response.body, 'avwiki-search')
            return
        if int(result[1][0]) != 1:
            self.log(('not found!! {}').format(result[1]))
            return
        href = response.css('h2.archive-header-title > a::attr(href)').extract_first()
        yield scrapy.Request(url=href, callback=self.parse_real_result)

    def parse_real_result(self, response):
        selectors = [
            'div.contents-box:contains("{}")',
            'div.col6 > p:contains("{}")',
        ]
        links = None
        for css in selectors:
            content = response.css(css.format(self.keyword.upper()))
            if len(content) > 0:
                links = content.css('a::attr(href)').extract()
                break
        self.log(links)
        if not links:
            self.log('could not parse html!')
            self.save_html(response.body, 'avwiki-real')
            return

        sites = {
            'www.mgstage.com':self.parse_movie_info, 
            'www.dmm.co.jp':self.parse_cid_list
        }
        links = set(links)
        item = JavItem()
        for link in list(links):
            domain = link.split('/')[2]
            if not sites.get(domain):
                self.log('unknown domain! %s' % domain)
                continue
            yield scrapy.Request(
                url = link,
                callback = sites[domain],
                cookies = self.cookies[domain],
                meta = {'item':item}
            )

    def parse_movie_info(self, response):
        from scrapy.loader import ItemLoader
        try:
            il = ItemLoader(item=response.meta['item'], response=response)
            il.add_css('title', 'div.common_detail_cover > h1.tag::text')
            il.add_css('thumb', '#EnlargeImage::attr(href)')
            il.add_xpath('studio',  '//th[contains(., "メーカー：")]/following-sibling::td/a/@href')
            il.add_xpath('runtime', '//th[contains(., "収録時間：")]/following-sibling::td/text()')
            il.add_xpath('id',      '//th[contains(., "品番：")]/following-sibling::td/text()')
            il.add_xpath('releasedate', '//th[contains(., "配信開始日：")]/following-sibling::td/text()')
            il.add_xpath('rating',  '//th[contains(., "評価：")]/following-sibling::td//text()')
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())

    def request_r18(self, response):
        r18 = 'http://www.r18.com/common/search/searchword='

        cids = response.meta['cids']
        self.log(cids)
        url = '%s%s'%(r18, cids.pop())
        self.log(url)
        yield scrapy.Request(
            url = url,
            callback=self.parse_r18_search_result,
            meta=response.meta)

    def parse_cid_list(self, response):
        results = response.css('p.tmb > a::attr(href)').extract()
        cids = [re.search(r'cid=(\w+)/', url).group(1) for url in results]
        if len(cids) == 0:
            self.log('no movie in dmm')
            return
        
        response.meta['cids'] = cids
        return self.request_r18(response)

    def parse_r18_search_result(self, response):
        results = response.css('ul.cmn-list-product01.type01 > li > a::attr(href)').extract()
        self.log(results)

        if len(results) == 1:
            self.log(results[0])
            yield scrapy.Request(url=results[0],
                callback = self.parse_actor_info,
                cookies = self.cookies['www.r18.com'],
                meta = response.meta
            )
        else:
            self.log('no exact matched id in r18! search next cid')
            return self.request_r18(response)

    def parse_actor_info(self, response):
        from scrapy.loader import ItemLoader
        try :
            il = ItemLoader(item=response.meta['item'], response=response)
            il.add_xpath('actor', '//label[contains(.,"Actress(es):")]/following-sibling::div[1]/span/a/span/text()')
            il.add_css('actor_thumb', 'ul.cmn-list-product03.clearfix.mr07 > li > a > p > img::attr(src)')
            return il.load_item()
        except:
            self.save_html(response.body)
            self.log(traceback.format_exc())