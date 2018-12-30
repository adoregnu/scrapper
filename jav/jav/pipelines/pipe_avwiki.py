
from .pipe_mgs import PipelineMgs

class PipelineAvwiki(PipelineMgs):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.completedMgs = False

    def process_item(self, item, spider):
        self.item = item
        if not self.completedMgs:
            super().process_item(item, spider)
            self.completedMgs = True
        else:
            self.list2str()
            self.filter('actor', lambda d: {'name':d, 'thumb':item['actor_thumb']})

        return item

