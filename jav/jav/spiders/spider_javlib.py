import os
import scrapy
import traceback
from .common import Common 
from jav.items import JavItem
class JavLibrary(scrapy.Spider, Common):
    name = "javlibrary"
    custom_settings = {
        'ITEM_PIPELINES': { 'jav.pipelines.pipe_javlib.PipelineJavlib': 300 },
        'CONCURRENT_REQUESTS' : 1 
    }

    def start_requests(self):
        url = 'http://www.javlibrary.com/en/vl_searchbyid.php'
        for id in self.cids:
            yield scrapy.Request(url='%s?keyword=%s'%(url, id['cid']),
                callback=self.parse, dont_filter=True, meta={'id':id})

    def parse(self, response):
        #self.save_html(response.body)
        videos = response.xpath('//div[@class="videos"]/div/a')
        if len(videos) == 0:
            return self.parse_result(response)

        id = response.meta['id']
        cid = id['cid'].upper()
        exactMatch = [v for v in videos if v.css('div.id::text').extract_first().upper() == cid]
        if len(exactMatch) > 0:
            url = response.urljoin(exactMatch[0].css('a::attr(href)').extract_first())
            self.log('url:%s' % url)
            return scrapy.Request(url=url, callback=self.parse_result, meta={'id':id})

    def parse_result(self, response):
        from scrapy.loader import ItemLoader
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