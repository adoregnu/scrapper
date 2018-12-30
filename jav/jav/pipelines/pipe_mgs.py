
from .pipe_comm import PipelineCommon

class PipelineMgs(PipelineCommon):
    def __init__(self, crawler):
        super().__init__(crawler)

    def process_item(self, item, spider):
        self.item = item
        self.filter('releasedate', self.slash2dash)
        self.filter('studio', lambda x:item[x][0].split('=')[1])
        self.filter('title', self.strip)
        self.filter('runtime', self.digit)
        self.filter('rating', lambda x: self.digit(''.join([i.strip() for i in item[x]])))
        self.list2str()
        return item