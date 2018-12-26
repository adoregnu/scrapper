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
        html = BeautifulSoup(item['set'], 'html.parser')
        setname = html.a.text.strip()
        if not setname.endswith('...'):
            item['set'] = setname
            return

        return scrapy.Request(url=html.a['href'], cookies = self.cookies)

    def return_item(self, response, item):
        item['set'] = response.css('div.cmn-ttl-tabMain01 > h1::text').extract_first()
        return item

    def actors(self, data, thumb):
        actors = []
        for i, item in enumerate(data):
            actor = {}
            m = re.search(r'([\w ]+)(\([\w ]+\))?', item)
            if m: 
                actor['name'] = m.group(1).strip()
                if m.group(2): actor['role'] = m.group(2)[1:-1]
            else:
                actor['name'] = item
            actor['thumb'] = thumb[i]
            actors.append(actor)
        return actors

    def convert_date(self, data):
        date = self.strip(data)
        m = re.search(r'([\w\.]+) (\d+), (\d+)', date)
        newdate = '%s %s %s'%(m.group(1)[0:3], m.group(2), m.group(3))
        self.log('old:%s new:%s'%(date, newdate))
        try:
            dt = datetime.strptime(newdate, r'%b %d %Y')
            return dt.strftime(r'%Y-%m-%d')
        except ValueError:
            pass

        self.log('unkown date format:{}'.format(date))
        return date

    def process_item(self, item, spider):
        item['genre'] = [i.strip() for i in item['genre']]
        self.filter(item, 'date', self.convert_date)
        item['director'] = self.strip(item['director'])
        item['label'] = self.strip(item['label'])
        item['runtime'] = self.digit(item['runtime'])
        item['studio'] = item['studio'][0].strip()
        self.filter(item, 'actor', lambda d: self.actors(d, item['actor_thumb']))

        self.list2str(item)
        request = self.check_full_set_name(item)
        if request:
            dfd = self.crawler.engine.download(request, spider)
            dfd.addBoth(self.return_item, item)
            return dfd
        else:
            return item