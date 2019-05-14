
from .pipe_comm import PipelineCommon

class PipelineDmm(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        self.filter(item, 'plot', self.strip)
        self.filter(item, 'runtime', self.digit)
        self.filter(item, 'releasedate', self.slash2dash)
        self.list2str(item)
        return item