from .pipe_mgs import PipelineMgs

class PipelineAvwiki(PipelineMgs):
    def __init__(self, crawler):
        super().__init__(crawler)
        self.completedMgs = False

    def process_item(self, item, spider):
        if not self.completedMgs:
            super().process_item(item, spider)
            self.completedMgs = True
        else:
            self.list2str(item)
            self.filter(item, 'actor', lambda it, d: {'name':it[d], 'thumb':it['actor_thumb']})

        return item