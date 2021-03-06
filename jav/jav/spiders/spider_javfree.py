import os, re
import scrapy
import traceback
from .common import Common 
from jav.items import JavItem

class JavFree(scrapy.Spider, Common):
    name = "javfree"
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_javfree.PipelineJavfree': 300 }
    }

    def start_requests(self):
        url = 'https://javfree.me/?s='
        for id in self.cids:
            yield scrapy.Request(url='%s%s'%(url, id['cid']), callback=self.parse_search, meta={'id':id})

    def parse_search(self, response):
        id = response.meta['id']
        url = response.css('h2.entry-title > a::attr(href)').extract_first()
        if url:
            yield scrapy.Request(url=url, callback=self.parse, meta={'id':id})
        else:
            self.log('{}:: not found {}.'.format(self.name, id['cid']))

    def parse(self, response):
        from scrapy.loader import ItemLoader

        fields = [
            ('title', 'h1.entry-title::text'),
            ('thumb', '//div[@class="entry-content"]/p/img[1]/@src'),
        ]

        avitem = JavItem()
        il = ItemLoader(item=avitem, response=response)
        self.initItemLoader(il, fields)

        res = response.css('div.entry-content > p::text').extract()
        line = ' '.join(res)
        m = re.search(r'(?:配信日|公開日|発売日|販売日|更新日):? (\d{4})(?:\D+)(\d{2})(?:\D+)(\d{2})', line)
        if m:
            il.add_value('releasedate', '-'.join(m.groups()))

        tags = response.css('div.entry-tags > span > a[rel="tag"]::text').extract()
        m = re.search(r'出演: ?(\w+)', line)
        if m:
            jname = m.group(1)
            #self.log(m.groups())
        else:
            jname = tags[0]
        id = response.meta['id']
        il.add_value('studio', tags[-1])
        il.add_value('id', id['cid'])

        self.log(tags)
        il.load_item()
        if len(tags) > 1:
            dmmurl = 'http://www.dmm.co.jp/search/=/searchstr={} 単体/'.format(jname)
            self.log(dmmurl)
            yield scrapy.Request(
                    url=dmmurl,
                    callback=self.parse_dmm_cid_list,
                    cookies=self.cookies['www.dmm.co.jp'],
                    meta={'item':avitem, 'il':il, 'id':id})