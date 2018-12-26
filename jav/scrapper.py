from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

class ScrapperWrapper:
    def __init__(self):
        configure_logging()
        self.runner = CrawlerRunner(get_project_settings())

    def callback(msg):
        print('done!', msg)

    #@defer.inlineCallbacks
    def crawl(spider, outdir, keyword):
        d = self.runner.crawl(spider, keyword=keyword, outdir=outdir)
        d.addBoth(self.callback)
        #reactor.stop()

'''
def start_reactor():
    reactor.runReturn()
    return stop_reactor

def stop_reactor():
    reactor.stop()
    print('stop_reactor')

def run_spider(spider, outdir, keyword):
    def f(q):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider, keyword=keyword, outdir=outdir)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
'''