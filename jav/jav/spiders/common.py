import re, os
import scrapy
import traceback
from scrapy.loader import ItemLoader

class Common:
    #outdir = './outdir'
    #keyword = '253KAKU-204'
    cids = []

    cookies = {
        'www.mgstage.com':[{'name':'adc', 'value':'1', 'domain':'mgstage.com', 'path':'/'}],
        'www.dmm.co.jp':[{'name':'cklg', 'value':'en', 'domain':'dmm.co.jp', 'path':'/'}],
        'www.r18.com' : [{'name':'lg', 'value':'en', 'domain':'r18.com', 'path':'/'}]
    }

    movieinfo = {}
    searched_cids = []

    def get_cid(self, k):
        numpartlen = len(k.split('-')[-1])
        if numpartlen == 3:
            cid = k.replace('-', '00')
        elif numpartlen == 4:
            cid = k.replace('-', '0')
        else:
            cid = k.replace('-','')
        return cid

    '''
    def get_out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)

    '''
    def save_html(self, body, cid):
        fname = '%s.html' % cid
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
            return #response.meta['item'].load_item()
        
        response.meta['cids'] = list(set(cids))
        return self.search_r18(response)

    def search_r18(self, response):
        r18 = 'http://www.r18.com/common/search/searchword='

        cids = response.meta['cids']
        self.log(cids)
        if not len(cids):
            self.log('search_r18:: no cids left')
            return

        while len(cids) > 0:
            cid = cids.pop()
            exact_cid = None
            try :
                exp = r'([a-zA-Z]+)(?:-|00)?([0-9]{3,5})(?:\D)?([0-9A-Fa-f])?'
                m = re.search(exp, cid)
                exact_cid = '-'.join([m.group(1), m.group(2)]).upper()
                if exact_cid in self.searched_cids:
                    self.log('same cid(%s) as previous search! skip!' % exact_cid)
                    continue
                else:
                    self.log('extracting %s from %s' % (exact_cid, cid))
                    break
            except Exception as e:
                self.log(e)

        if not exact_cid:
            self.log('no cid suited for seaching!')
            return

        url = '%s%s'%(r18, exact_cid)
        self.searched_cids.append(exact_cid)
        self.log('searching cid from R18 %s' % url)
        return scrapy.Request(
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
        try :
            actor_xpath = '//label[contains(.,"Actress(es):")]/following-sibling::div[1]/span/a/span/text()'
            actor = response.xpath(actor_xpath).extract_first()
            print('parse_r18_actor_info ::', actor)
            if actor == None:
                return self.search_r18(response)
            il = ItemLoader(item=response.meta['item'], response=response)
            il.add_xpath('actor', actor_xpath)
            il.add_css('actor_thumb', 'ul.cmn-list-product03.clearfix.mr07 > li > a > p > img::attr(src)')
            return il.load_item()
        except:
            #self.save_html(response.body)
            self.log(traceback.format_exc())
