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
#        self.item = None
#        self.outdir = None
#        self.keyword = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    '''
    def open_spider(self, spider):
        self.outdir = spider.outdir
        self.keyword = spider.keyword

    def close_spider(self, spider):
        spider.movieinfo = dict(self.item)
        spider.movieinfo['path'] = spider.outdir
        if 'releasedate' in spider.movieinfo:
            spider.movieinfo['year'] = spider.movieinfo['releasedate'].split('-')[0]
        if 'actor_thumb' in spider.movieinfo:
            del spider.movieinfo['actor_thumb']
    '''

    def log(self, msg):
        self.logger.info(msg)

    '''
    @property
    def out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)
    '''

    def filter(self, item, kw, func):
        try:
            ret = func(item, kw)
            if ret: item[kw] = ret
        except Exception as e:
            self.log('filter:{}'.format(e))

    def strip(self, item, kw):
        if isinstance(item[kw], list):
            return ''.join(item[kw]).strip()
        else:
            return item[kw].strip()

    def digit(self, item, kw):
        item[kw] = self.strip(item, kw)
        return re.search(r'([\d\.]+)', item[kw]).group(1)

    def slash2dash(self, item, kw):
        item[kw] = self.strip(item, kw)
        return '-'.join(item[kw].split('/'))

    '''
    def save_html(self, body, fname = None):
        if not fname:
            fname = '%s/%s.html'%(self.out_path, self.keyword)
        with open(fname, 'wb') as (f):
            f.write(body)
            self.logger.info('Saved file %s'% fname)
    '''

    def list2str(self, item):
        for k in item.fields:
            if not k in item: continue
            if not isinstance(item[k], list): continue
            if len(item[k]) > 1: continue

            if 'thumb' == k:
                item[k] = AvImage(item[k][0])
            else:
                item[k] = item[k][0]