from .pipe_comm import PipelineCommon

class PipelineJavfree(PipelineCommon):
    donotcrop = ['heyzo','1pondo', 'Carib', 'caribpr', 'pacopacomama']
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        self.list2str(item)
        self.filter(item, 'actor', lambda it, d: {'name':it[d], 'thumb':it['actor_thumb']})
        #if item['studio'] in self.donotcrop:
        title = item['title']
        pos = title.find(item['id'])
        item['title'] = title[len(item['id']) + pos+1:].strip()
        return item