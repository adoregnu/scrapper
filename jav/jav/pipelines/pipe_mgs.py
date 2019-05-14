
from .pipe_comm import PipelineCommon

class PipelineMgs(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        self.filter(item, 'releasedate', self.slash2dash)
        self.filter(item, 'studio', lambda it, x:it[x][0].split('=')[1])
        self.filter(item, 'title', self.strip)
        self.filter(item, 'runtime', self.digit)
        self.filter(item, 'rating', self.digit)
        self.list2str(item)
        return item