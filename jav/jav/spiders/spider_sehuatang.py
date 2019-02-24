import os
import scrapy
import traceback
from .common import Common
#from jav.items import JavItem
from jav.items import Article

class Sehuatang(scrapy.Spider, Common):
    name = 'sehuatang'
    custom_settings = {
        'ITEM_PIPELINES': {
            #'jav.pipelines.pipe_torrent.PipelineBaiHao':1,
            'jav.pipelines.pipe_torrent.PipelineTorrent':2,
            'jav.pipelines.pipe_torrent.PipelinePreview':3,
        },
        'FILES_STORE' : 'sehuatang',
        'IMAGES_STORE' : 'sehuatang'
    }
    num_page = 1

    def start_requests(self):
        import datetime
        dt = datetime.datetime.now()
        self.outdir = 'g:/tmp/%s/sehuatang' % dt.strftime('%Y-%m-%d')
        os.makedirs(self.outdir, exist_ok=True)
        self.url = 'https://www.sehuatang.org/'
        yield scrapy.Request(url=self.url, callback = self.parse_main)

    def parse_main(self, response):
        sensored = response.xpath('//a[contains(., "亚洲有码原创")]/@href').extract_first()
        yield scrapy.Request(url='%s%s' % (self.url, sensored), callback=self.parse_list, meta={'page':1})

    def parse_list(self, response):
        #self.save_html(response.body, 'list')
        articles = response.xpath('//tbody[contains(@id, "normalthread_")]/tr/td/a/@href').extract()
        for i, article in enumerate(articles):
            yield scrapy.Request(url = '%s%s'%(self.url, article), callback=self.parse_article, meta={'count':i})

        if response.meta['page'] > 1 or self.num_page < 2:
            return

        pages = response.xpath('//span[@id="fd_page_top"]/div/a/@href').extract()
        #self.log(pages)
        pages = pages[0:self.num_page - 1]
        for i, page in enumerate(pages):
            yield scrapy.Request(url = '%s%s'%(self.url, page), callback=self.parse_list, meta={'page':i+2})

    def parse_article(self, response):
        #self.save_html(response.body, 'article')
        from scrapy.loader import ItemLoader
        il = ItemLoader(item = Article(), response=response)
        il.add_xpath('id', '//span[@id="thread_subject"]/text()', re=r'([a-z0-9\-_]+)')
        il.add_xpath('file_name', '//a[contains(., ".torrent")]/text()')
        il.add_xpath('file_urls', '//a[contains(., ".torrent")]/@href')
        il.add_xpath('image_urls', '//td[contains(@id, "postmessage_")]//img[contains(@id, "aimg_")]/@file')
        return il.load_item()
