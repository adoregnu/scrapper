import re
import os, logging
from PIL import Image
from xml.etree.ElementTree import fromstring, ElementTree, SubElement

from jav.utils import AvImage
from jav.items import JavItem

class PipelineCommon(object):
    logger = logging.getLogger(__name__)
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.item = JavItem()
        self.outdir = None
        self.keyword = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.outdir = spider.outdir
        self.keyword = spider.keyword

    def close_spider(self, spider):
        spider.movieinfo = dict(self.item)
        if 'releasedate' in spider.movieinfo:
            spider.movieinfo['year'] = spider.movieinfo['releasedate'].split('-')[0]
        if 'actor_thumb' in spider.movieinfo:
            del spider.movieinfo['actor_thumb']

    def log(self, msg):
        self.logger.info(msg)

    @property
    def out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)

    def filter(self, kw, func):
        try:
            ret = func(kw)
            if ret: self.item[kw] = ret
        except Exception as e:
            self.log('filter:{}'.format(e))

    def strip(self, kw):
        if isinstance(self.item[kw], list):
            return ''.join(self.item[kw]).strip()
        else:
            return self.item[kw].strip()

    def digit(self, kw):
        self.item[kw] = self.strip(kw)
        return re.search(r'([\d\.]+)', self.item[kw]).group(1)

    def slash2dash(self, kw):
        self.item[kw] = self.strip(kw)
        return '-'.join(self.item[kw].split('/'))

    def save_html(self, body, fname = None):
        if not fname:
            fname = '%s/%s.html'%(self.out_path, self.keyword)
        with open(fname, 'wb') as (f):
            f.write(body)
            self.logger.info('Saved file %s'% fname)

    def list2str(self):
        for k in self.item.fields:
            if not k in self.item: continue
            if not isinstance(self.item[k], list): continue
            if len(self.item[k]) > 1: continue

            if 'thumb' == k:
                self.item[k] = AvImage(self.item[k][0])
            else:
                self.item[k] = self.item[k][0]