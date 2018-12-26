import os

class Common():
    outdir = './outdir'
    keyword = '253KAKU-204'

    cookies = {
        'www.mgstage.com':[{'name':'adc', 'value':'1', 'domain':'mgstage.com', 'path':'/'}],
        'www.dmm.co.jp':[{'name':'cklg', 'value':'en', 'domain':'dmm.co.jp', 'path':'/'}],
        'www.r18.com' : [{'name':'lg', 'value':'en', 'domain':'r18.com', 'path':'/'}]
    }

    def prepare_request(self):
        targetdir = '/'.join([self.outdir, self.keyword])
        os.makedirs(targetdir, exist_ok=True)
        if isinstance(self.keyword, str):
            kws = [self.keyword]
        else:
            kws = self.keyword
        return kws

    def get_cid(self, k = None):
        if not k: k = self.keyword
        if len(k.split('-')[-1]) > 3:
            cid = k.replace('-', '0')
        else:
            cid = k.replace('-', '00')
        return cid

    def get_out_path(self):
        return '%s/%s' % (self.outdir, self.keyword)

    def save_html(self, body, fname = None):
        fname = self.keyword if not fname else fname
        fname = '%s/%s.html' % (self.get_out_path(), fname)
        with open(fname, 'wb') as (f):
            f.write(body)
            self.log('Saved file %s' % fname)



