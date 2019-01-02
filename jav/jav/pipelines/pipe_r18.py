import re
import scrapy
from datetime import datetime
from .pipe_comm import PipelineCommon

class PipelineR18(PipelineCommon):
    cookies = [{'name':'lg', 'value':'en', 'domain':'r18.com', 'path':'/'}]

    def __init__(self, crawler):
        super().__init__(crawler)

    def check_full_set_name(self):
        if not 'set' in self.item: return None

        from bs4 import BeautifulSoup
        html = BeautifulSoup(str(self.item['set']), 'html.parser')
        setname = html.a.text.strip()
        if not setname.endswith('...'):
            self.item['set'] = setname
            return

        return scrapy.Request(url=html.a['href'], cookies = self.cookies)

    def return_item(self, response):
        self.item['set'] = response.css('div.cmn-ttl-tabMain01 > h1::text').extract_first()
        return self.item

    def actors(self, kw):
        from jav.utils import AvImage
        from jav.actor_map import adjust_actor
        actors = []
        for i, item in enumerate(self.item[kw]):
            actor = {}
            m = re.search(r'([\w ]+)(\([\w ]+\))?', item)
            if m: 
                actor['name'] = m.group(1).strip()
                if m.group(2): actor['role'] = m.group(2)[1:-1]
            else:
                actor['name'] = item
            actor['name'] = adjust_actor(actor['name'])
            actor['thumb'] = AvImage(self.item['actor_thumb'][i])
            actors.append(actor)
        return actors

    def convert_date(self, kw):
        self.item[kw] = self.strip(kw)
        m = re.search(r'([\w\.]+) (\d+), (\d+)', self.item[kw])
        newdate = '%s %s %s'%(m.group(1)[0:3], m.group(2), m.group(3))
        #self.log('old:%s new:%s'%(self.item[kw], newdate))
        try:
            dt = datetime.strptime(newdate, r'%b %d %Y')
            return dt.strftime(r'%Y-%m-%d')
        except ValueError:
            self.log('unkown date format:{}'.format(self.item[kw]))


    def process_item(self, item, spider):
        self.item = item
        self.filter('genre', lambda x:[i.strip() for i in item[x]])
        self.filter('studio', lambda x:item[x][0].strip())
        self.filter('releasedate', self.convert_date)
        self.filter('director', self.strip)
        self.filter('label', self.strip)
        self.filter('runtime', self.digit)
        self.filter('actor', self.actors)

        self.list2str()
        request = self.check_full_set_name()
        if request:
            dfd = self.crawler.engine.download(request, spider)
            dfd.addBoth(self.return_item)
            return dfd
        else:
            return item