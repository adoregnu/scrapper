
from .pipe_comm import PipelineCommon

class PipelineMgs(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        item['date'] = self.slash2dash(item['date'])
        item['studio'] = item['studio'][0].split('=')[1]
        item['title'] = self.strip(item['title'])
        item['runtime'] = self.digit(item['runtime'])
        item['rating'] = self.digit(''.join([i.strip() for i in item['rating']]))

        self.list2str(item)
        return item