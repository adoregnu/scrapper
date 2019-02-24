
import os, logging
import scrapy
from .pipe_comm import PipelineCommon
from scrapy.pipelines.images import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

def log(msg):
    logging.getLogger(__name__).info(msg)

class PipelineTorrent(FilesPipeline):
    def get_media_requests(self, item, info):
        for i, file_url in enumerate(item['file_urls']):
            url = '%s%s' % (info.spider.url, file_url)
            #log(url)
            yield scrapy.Request(url=url, meta={
                'outdir':info.spider.outdir, 'file_name':item['file_name'][i], 'id':item['id'][0]})

    def file_path(self, request, response=None, info=None):
        meta = request.meta
        #log(meta)
        return '%s/%s/%s' % (meta['outdir'], meta['id'], meta['file_name'])

class PipelinePreview(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={
            'outdir':info.spider.outdir,'id':item['id'][0], 'name':os.path.basename(x)})
                for x in item.get(self.images_urls_field, [])]

    def file_path(self, request, response=None, info=None):
        meta = request.meta
        return '%s/%s/%s' % (meta['outdir'], meta['id'], meta['name'])

class PipelineBaiHao:
    def process_item(self, item, spider):
        #os.makedirs('%s/%s' % (spider.outdir, item['id']), exist_ok=True)
        item['file_urls'].extend(item['cover_img_url'])
        item['file_name'].extend(item['cover_img_name'])

        return item