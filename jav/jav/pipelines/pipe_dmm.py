
from .pipe_comm import PipelineCommon

class PipelineDmm(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        item['plot'] = self.strip(item['plot'])
        item['runtime'] = self.digit(item['runtime'])
        item['date'] = self.slash2dash(item['date'])
        return item