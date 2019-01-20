import re, os
import scrapy
import traceback


class Common():
    outdir = './outdir'
    keyword = '253KAKU-204'

    cookies = {
        'www.mgstage.com':[{'name':'adc', 'value':'1', 'domain':'mgstage.com', 'path':'/'}],
        'www.dmm.co.jp':[{'name':'cklg', 'value':'en', 'domain':'dmm.co.jp', 'path':'/'}],
        'www.r18.com' : [{'name':'lg', 'value':'en', 'domain':'r18.com', 'path':'/'}]
    }

    movieinfo = {}

    def prepare_request(self):
        #targetdir = '/'.join([self.outdir, self.keyword])
        #os.makedirs(targetdir, exist_ok=True)
        if isinstance(self.keyword, str):
            kws = [self.keyword]
        else:
            kws = self.keyword
        return kws

    def get_cid(self, k = None):
        if not k: k = self.keyword
        numpartlen = len(k.split('-')[-1])
        if numpartlen == 3:
            cid = k.replace('-', '00')
        elif numpartlen == 4:
            cid = k.replace('-', '0')
        else:
            cid = k.replace('-','')
        return cid

    def get_out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)

    def save_html(self, body, fname = None):
        fname = self.keyword if not fname else fname
        fname = '%s/%s.html' % (self.outdir, fname)
        with open(fname, 'wb') as (f):
            f.write(body)
            self.log('Saved file %s' % fname)

    def initItemLoader(self, il, fields):
        add = lambda fn, f: \
            fn(f[0], f[1], re=f[2]) if len(f) == 3 else \
            fn(f[0], f[1])

        for field in fields:
            if field[1].startswith('//'): 
                add(il.add_xpath, field)
                #il.add_xpath(field[0], field[1])
            else:
                add(il.add_css, field)
                #il.add_css(field[0], field[1])

    def get_dmm_cids(self, response):
        results = response.css('p.tmb > a::attr(href)').extract()
        #self.log('common::get_dmm_cids: {}'.format(results))
        cids = [re.search(r'cid=(\w+)/', url).group(1) for url in results]
        if len(cids) == 0:
            self.log('no movie in dmm')
        return results, cids
 
    def parse_dmm_cid_list(self, response):
        _, cids = self.get_dmm_cids(response)
        if len(cids) == 0:
            return
        
        response.meta['cids'] = list(set(cids))
        return self.search_r18(response)

    def search_r18(self, response):
        r18 = 'http://www.r18.com/common/search/searchword='

        cids = response.meta['cids']
        self.log(cids)
        if not len(cids):
            self.log('search_r18:: no cids left')
            return

        url = '%s%s'%(r18, cids.pop())
        self.log(url)
        yield scrapy.Request(
            url = url,
            callback=self.parse_r18_search_result,
            meta=response.meta)

    def parse_r18_search_result(self, response):
        results = response.css('ul.cmn-list-product01.type01 > li > a::attr(href)').extract()
        self.log(results)

        if len(results) == 1:
            self.log(results[0])
            return scrapy.Request(url=results[0],
                callback = self.parse_r18_actor_info,
                cookies = self.cookies['www.r18.com'],
                meta = response.meta
            )
        else:
            self.log('parse_r18_search_result:: no exact matched id in r18! search next cid')
            return self.search_r18(response)

    def parse_r18_actor_info(self, response):
        from scrapy.loader import ItemLoader
        try :
            il = ItemLoader(item=response.meta['item'], response=response)
            il.add_xpath('actor', '//label[contains(.,"Actress(es):")]/following-sibling::div[1]/span/a/span/text()')
            il.add_css('actor_thumb', 'ul.cmn-list-product03.clearfix.mr07 > li > a > p > img::attr(src)')
            return il.load_item()
        except:
            #self.save_html(response.body)
            self.log(traceback.format_exc())
