import re
import scrapy
from datetime import datetime
from .pipe_comm import PipelineCommon

class PipelineR18(PipelineCommon):
    cookies = [{'name':'lg', 'value':'en', 'domain':'r18.com', 'path':'/'}]

    def __init__(self, crawler):
        super().__init__(crawler)

    def check_full_set_name(self, item):
        if not 'set' in item: return None

        from bs4 import BeautifulSoup
        html = BeautifulSoup(str(item['set']), 'html.parser')
        setname = html.a.text.strip()
        if not setname.endswith('...'):
            item['set'] = setname
            return

        return scrapy.Request(url=html.a['href'], cookies = self.cookies)

    def return_item(self, response, item):
        item['set'] = response.css('div.cmn-ttl-tabMain01 > h1::text').extract_first()
        return item

    def actors(self, item, kw):
        from jav.utils import AvImage
        from jav.actor_map import adjust_actor
        actors = []
        for i, it in enumerate(item[kw]):
            actor = {}
            m = re.search(r'([\w ]+)(\([\w ]+\))?', it)
            if m: 
                actor['name'] = m.group(1).strip()
                if m.group(2): actor['role'] = m.group(2)[1:-1]
            else:
                actor['name'] = it
            actor['name'] = adjust_actor(actor['name'])
            actor['thumb'] = AvImage(item['actor_thumb'][i])
            actors.append(actor)
        return actors

    def convert_date(self, item, kw):
        item[kw] = self.strip(item, kw)
        m = re.search(r'([\w\.]+) (\d+), (\d+)', item[kw])
        newdate = '%s %s %s'%(m.group(1)[0:3], m.group(2), m.group(3))
        #self.log('old:%s new:%s'%(self.item[kw], newdate))
        try:
            dt = datetime.strptime(newdate, r'%b %d %Y')
            return dt.strftime(r'%Y-%m-%d')
        except ValueError:
            self.log('unkown date format:{}'.format(item[kw]))


    def process_item(self, item, spider):
        self.filter(item, 'genre', lambda it, x:[i.strip() for i in it[x]])
        self.filter(item, 'studio', lambda it, x:it[x][0].strip())
        self.filter(item, 'releasedate', self.convert_date)
        self.filter(item, 'director', self.strip)
        self.filter(item, 'label', self.strip)
        self.filter(item, 'runtime', self.digit)
        self.filter(item, 'actor', self.actors)

        self.list2str(item)
        request = self.check_full_set_name(item)
        if request:
            dfd = self.crawler.engine.download(request, spider)
            dfd.addBoth(self.return_item, item=item)
            return dfd
        else:
            return item