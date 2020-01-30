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

        href = None
        for link in response.css('h2.archive-header-title > a::attr(href)').extract():
            self.log(link)
            if link  ==  'https://shecool.net/av-wiki/': continue
            if '/av-actress/' in link: continue

            href = link
            break

        if not href: return
        yield scrapy.Request(url=href, callback=self.parse_real_result, meta=response.meta)

    def parser1(self, content):
        link = content.css('div.item-header1 > p > a::attr(href)').extract_first()
        if not link:
            link = content.css('div.item-header > p > a::attr(href)').extract_first()
        actor = content.css('div.s-contents > p *::text').extract()[1]
        self.log('actor:{}, link:{}'.format(actor, link))
        return link, actor

    def parser2(self, content):
        self.log('not implemented!')
        return None, None

    def parse_real_result(self, response):
        selectors = [
            {'css':'div.contents-box:contains("{}")', 'parser':self.parser1},
            {'css':'div.col6 > p:contains("{}")', 'parser':self.parser2}
        ]

        id = response.meta['id']
        cid = id['cid'].upper()
        link = None
        actor = None
        for css in selectors:
            content = response.css(css['css'].format(cid))
            if len(content) > 0:
                link, actor = css['parser'](content)
                break

        if not link:
            self.log('could not parse html!')
            self.save_html(response.body, 'avwiki-real')
            return

        #process link
        item = JavItem()
        domain = link.split('/')[2]
        yield scrapy.Request(
            url = link,
            callback = self.parse_movie_info,
            cookies = self.cookies[domain],
            meta = {'item':item, 'id':id}
        )

        #process actor
        if not actor or actor == '＊＊＊': return
        for act in actor.split('　'):
            dmm_search_url = 'https://www.dmm.co.jp/search/=/searchstr=%s 単体' % act
            yield scrapy.Request(
                url = dmm_search_url,
                callback = self.parse_dmm_cid_list,
                cookies = self.cookies['www.dmm.co.jp'],
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