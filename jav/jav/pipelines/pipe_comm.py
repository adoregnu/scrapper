import re
import os, logging
from PIL import Image
from xml.etree.ElementTree import fromstring, ElementTree, SubElement

from jav.utils import indent_xml, XML_TEMPLATE

class PipelineCommon(object):
    logger = logging.getLogger(__name__)
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.item = None
        self.outdir = None
        self.keyword = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        #self.log('open_spider outdir:%s, keyword:%s'%(spider.outdir, spider.keyword))
        self.root = fromstring(XML_TEMPLATE)
        self.outdir = spider.outdir
        self.keyword = spider.keyword

    def close_spider(self, spider):
        #self.log('close_spider')
        if not self.item: return
        for k in self.item.fields:
            if k == 'thumb' and k in self.item:
                self.prepare_fanart_poster(spider)
            if k == 'actor_thumb' and k in self.item:
                self.prepare_actor_image()

            self.append_element(k, self.item.get(k))

        indent_xml(self.root)
        tree = ElementTree(self.root)
        tree.write('{0}/{1}/{1}.nfo'.format(spider.outdir, spider.keyword),
            encoding = 'UTF-8', xml_declaration = True)

    def log(self, msg):
        self.logger.info(msg)

    @property
    def out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)

    def filter(self, item, kw, func):
        try:
            item[kw] = func(item[kw])
        except Exception as e:
            self.log('filter:{}'.format(e))

    def strip(self, data):
        return ''.join(data).strip()

    def digit(self, data):
        return re.search(r'([\d\.]+)', self.strip(data)).group(1)

    def slash2dash(self, data):
        return '-'.join(self.strip(data).split('/'))

    def save_html(self, body, fname = None):
        if not fname:
            fname = '%s/%s.html'%(self.out_path, self.keyword)
        with open(fname, 'wb') as (f):
            f.write(body)
            self.logger.info('Saved file %s'% fname)

    def list2str(self, item):
        self.item = item
        for k in item.fields:
            if item.get(k) and isinstance(item[k], list) and len(item[k]) == 1:
                item[k] = item[k][0]

    def append_element(self, key, data):
        if key == 'genre' and data:
            for genre in data:
                SubElement(self.root, key).text = genre
        elif key == 'actor' and data:
            if isinstance(data, str):
                elm = SubElement(self.root, key)
                SubElement(elm, 'name').text = data
            if isinstance(data, dict):
                elm = SubElement(self.root, key)
                for k, v in data.items():
                    SubElement(elm, k).text = v
            if isinstance(data, list):
                for item in data:
                    elm = SubElement(self.root, key)
                    if isinstance(item, dict):
                        for k, v in item.items():
                            SubElement(elm, k).text = v
                    else:
                        SubElement(elm, 'name').text = item
        elif isinstance(data, str):
            if key == 'date':
                SubElement(self.root, 'year').text = data.split('-')[0]
                key = 'releasedate'
            SubElement(self.root, key).text = data
        else:
            self.log('invalid data!  key:{}, data:{}'.format(key, data))

    def download_file(self, url, fname):
        import requests
        try:
            res = requests.get(url, timeout=10)
            self.log('save %s' % fname)
            with open(fname, 'wb') as f:
                f.write(res.content)
            return fname
        except Exception as e:
            self.log('failed to download thumb:%s'%str(e))

    def download_cover_image(self, url):
        ext = url.split('.')[-1]
        fanart = '%s/%s-fanart.%s' %(self.out_path, self.keyword, ext)
        return self.download_file(url, fanart)

    def download_actor_image(self, url):
        outdir = '%s/.actors' % self.out_path
        os.makedirs(outdir, exist_ok=True)
        fname = '%s/%s' % (outdir, os.path.basename(url))
        return self.download_file(url, fname)

    def crop_image_left(self, path, ratio=0.475):
        ext = path.split('.')[-1]
        im = Image.open(path)
        w, h = im.size
        cim = im.crop((w - w*ratio, 0, w, h))
        poster = '%s/%s-poster.%s'%(self.out_path, self.keyword, ext)
        cim.save(poster)
        return poster

    def rotate_image(self, path, degree = Image.ROTATE_90):
        ext = path.split('.')[-1]
        im = Image.open(path)
        rim = im.transpose(degree)
        poster = '%s/%s-poster.%s' %(self.out_path, self.keyword, ext)
        rim.save(poster)
        return poster

    def prepare_fanart_poster(self, spider):
        res = self.download_cover_image(self.item['thumb'])
        if not res:
            return

        if spider.name == 'avwiki' or spider.name == 'mgstage':
            if spider.keyword.upper().startswith('259LUXU'):
                self.crop_image_left(res, 0.5)
            else:
                degree = Image.ROTATE_90
                self.rotate_image(res, degree)
        else: 
            self.crop_image_left(res)

    def prepare_actor_image(self):
        if isinstance(self.item['actor_thumb'], str):
            if not 'nowprinting' in self.item['actor_thumb']:
                self.download_actor_image(self.item['actor_thumb'])
        else:
            for url in self.item['actor_thumb']:
                if 'nowprinting' in url: continue
                self.download_actor_image(url)