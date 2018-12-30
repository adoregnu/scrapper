
from .pipe_comm import PipelineCommon

class PipelineDmm(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        self.item = item
        self.filter('plot', self.strip)
        self.filter('runtime', self.digit)
        self.filter('releasedate', self.slash2dash)
        self.list2str()
        return item