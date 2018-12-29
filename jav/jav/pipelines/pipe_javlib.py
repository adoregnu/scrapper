
from .pipe_comm import PipelineCommon

class PipelineJavlib(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def parse_actors(self, html):
        from bs4 import BeautifulSoup
        html = BeautifulSoup(html[0], 'html.parser')
        actors = []
        for cast in html.select('.cast'):
            actor = {}
            name = cast.select('.star')[0].text.split(' ')
            name.reverse()
            actor['name'] = ' '.join(name)
            alias = cast.select('.alias')
            if len(alias) > 0:
                actor['role'] = []
                for item in alias:
                    name = item.text.split(' ')
                    name.reverse()
                    actor['role'].append(' '.join(name))
            actors.append(actor)
        return actors

    def process_item(self, item, spider):
        self.filter(item, 'actor', self.parse_actors)
        item['thumb'] = 'http:%s'%item['thumb'][0]
        self.filter(item, 'rating', self.digit)

        self.list2str(item)
        item['title'] = item['title'].replace(item['id'], '').strip()
        return item

