from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import ads
import sys
import time
import numpy as np
import pickle
import shutil
import requests
import unicodedata as ud

if sys.version_info[0] > 2:
    input_line = input
else:
    input_line = raw_input


def get_adsurl_from_bibtex(bibtex):
    for i in bibtex.split('\n'):
        if i.replace(' ', '').split('=')[0] == 'adsurl':
            return i.replace(' ', '').split('{')[1].split('}')[0]


class DataBase:

    def __init__(self):
        
        self.here = os.path.abspath(os.path.dirname(__file__))
        self.database_path = os.path.join(self.here, 'my_library.pickle')
        self.bib_path = os.path.join(self.here, 'my_library.bib')

        if os.path.isfile(self.database_path):
            self.database = pickle.load(open(self.database_path, 'rb'))
        else:
            self.database = {}

        self.token_file = os.path.join(self.here, 'token.txt')
        if os.path.isfile(self.token_file):
            self.token = open(self.token_file).readlines()[0].split()[0]
            ads.config.token = '{0}'.format(self.token)
        else:
            self.token = input_line('   Please provide token. To obtain a token please: \n' +
                                    '   1. Visit https://ui.adsabs.harvard.edu/ \n' +
                                    '   2. Log in \n' +
                                    '   3. Go to Account -> Customize settings (up right) \n' +
                                    '   4. Go to API Token (down left) \n' +
                                    '   5. Click on Generate a new key \n' +
                                    '   6. Copy the new key here. \n')
            ads.config.token = self.token
            w = open(self.token_file, 'w')
            w.write(self.token)
            w.close()

    def add_to_library(self, bibcode):

        if len(bibcode.split('arXiv')) == 2:
            print(bibcode)
            try:
                connection = 0
                while connection == 0:
                    try:
                        ads_paper = list(ads.SearchQuery(alternate_bibcode=bibcode, fl=['bibcode']))[0]
                        try:
                            del self.database[bibcode]
                        except KeyError:
                            pass
                        bibcode = ads_paper.bibcode
                        connection = 1
                        time.sleep(1)
                    except requests.ConnectionError:
                        time.sleep(1)       
            except IndexError:
                pass
        else:
            pass
    
        if bibcode not in self.database:
            connection = 0
            while connection == 0:
                try:
                    a = ads.SearchQuery(bibcode=bibcode, fl=['adsurl', 'title', 'author', 'abstract'])
                    a = list(a)[0]
                    b = ads.ExportQuery(bibcodes=bibcode, format="bibtex").execute()
                    connection = 1
                    self.database[bibcode] = {'adsurl': get_adsurl_from_bibtex(b),
                                              'title': a.title,
                                              'author': a.author, 'abstarct': a.abstract,
                                              'bibtex': b,
                                              'call': bibcode}

                    old_call = self.database[bibcode]['call']
                    new_call = a.author[0].split(',')[0].replace(' ', '').replace('-', '') + bibcode[:4]
                    new_call = ud.normalize('NFKD', new_call).encode('ascii', 'ignore')
                    self.database[bibcode]['bibtex'] = \
                        self.database[bibcode]['bibtex'].replace('{' + old_call, '{' + new_call)
                    self.database[bibcode]['call'] = new_call

                    calls = [self.database[ff]['call'].split('B')[0] for ff in self.database]
                    for i in self.database:
                        if calls.count(self.database[i]['call']) > 1:
                            old_call = self.database[i]['call']
                            new_call = self.database[i]['call'].split('B')[0] + 'B' + i
                            new_call = new_call.replace('&', 'a')
                            self.database[i]['bibtex'] = \
                                self.database[i]['bibtex'].replace('{' + old_call, '{' + new_call)
                            self.database[i]['call'] = new_call

                except requests.ConnectionError:
                    time.sleep(1)

        self.update_library_pickle()

        self.update_library_bib()

    def multi_add_to_library(self, bibcodes):

        for nbib, bibcode in enumerate(bibcodes):

            if len(bibcode.split('arXiv')) == 2:
                try:
                    connection = 0
                    while connection == 0:
                        try:
                            ads_paper = list(ads.SearchQuery(alternate_bibcode=bibcode, fl=['bibcode']))[0]
                            try:
                                del self.database[bibcode]
                            except KeyError:
                                pass
                            bibcodes[nbib] = ads_paper.bibcode
                            connection = 1
                        except requests.ConnectionError:
                            time.sleep(1)
                except IndexError:
                    pass
            else:
                pass

        bibcodes = list(np.unique(bibcodes))

        bibcodes_to_include = []
        for i in bibcodes:
            if i not in self.database:
                bibcodes_to_include.append(i)

        connection = 0
        bibtexs_to_include = [ff for ff in bibcodes_to_include]
        while connection == 0:
            try:
                print('connecting...')
                bibtexs_to_include = ads.ExportQuery(bibcodes=bibcodes_to_include, format='bibtex').execute()
                bibtexs_to_include = bibtexs_to_include.split('\n\n')[:-1]
                connection = 1
            except requests.ConnectionError:
                time.sleep(1)

        bibcodes_to_include = [str(ff.split('\n')[0].split('{')[1][:-1]) for ff in bibtexs_to_include]

        print('bibtexs loaded')
        for nbib, bibcode in enumerate(bibcodes_to_include):
            print(bibcode)
            if bibcode not in self.database:
                connection = 0
                while connection == 0:
                    try:
                        a = ads.SearchQuery(bibcode=bibcode, fl=['adsurl', 'title', 'author', 'abstract'])
                        a = list(a)[0]
                        b = bibtexs_to_include[nbib]
                        connection = 1
                        self.database[bibcode] = {'adsurl': get_adsurl_from_bibtex(b),
                                                  'title': a.title,
                                                  'author': a.author, 'abstarct': a.abstract,
                                                  'bibtex': b,
                                                  'call': bibcode}

                        old_call = self.database[bibcode]['call']
                        new_call = a.author[0].split(',')[0].replace(' ', '').replace('-', '') + bibcode[:4]
                        new_call = ud.normalize('NFKD', new_call).encode('ascii', 'ignore')
                        new_call = new_call.replace('&', 'a')
                        self.database[bibcode]['bibtex'] = \
                            self.database[bibcode]['bibtex'].replace('{' + old_call, '{' + new_call)
                        self.database[bibcode]['call'] = new_call
                    except requests.ConnectionError:
                        time.sleep(1)

        calls = [self.database[ff]['call'].split('B')[0] for ff in self.database]
        for i in self.database:
            if calls.count(self.database[i]['call']) > 1:
                old_call = self.database[i]['call']
                new_call = self.database[i]['call'].split('B')[0] + 'B' + i
                new_call = new_call.replace('&', 'a')
                self.database[i]['bibtex'] = \
                    self.database[i]['bibtex'].replace('{' + old_call, '{' + new_call)
                self.database[i]['call'] = new_call

        self.update_library_pickle()

        self.update_library_bib()

    def replace_splitter(self, old, new):

        for i in self.database:
            old_call = self.database[i]['call']
            new_call = old_call.replace(old, new)
            self.database[i]['bibtex'] = \
                self.database[i]['bibtex'].replace('{' + old_call, '{' + new_call)
            self.database[i]['call'] = self.database[i]['call'].replace(old, new)

        self.update_library_pickle()

        self.update_library_bib()

    def update_library_pickle(self):

        pickle.dump(self.database, open(self.database_path, 'wb'))

    def update_library_bib(self):

        w = open(self.bib_path, 'w')
        for i in self.database:
            bibtex = self.database[i]['bibtex']
            bibtex = bibtex.replace('{\\$}\\eta{\\_}{\\{}\\mathrm{\\{}\\oplus{\\}}{\\}}{\\$}', '$\\eta_\\oplus$')
            bibtex = bibtex.replace('$\\lt$', '$<$')
            bibtex = bibtex.replace('$\\gt$', '$>$')
            w.write(bibtex)
            w.write('\n\n\n')
        w.close()

    def update_library(self):

        for i in list(self.database):
            self.add_to_library(i)

    def search_library(self, bibcode):

        if bibcode in self.database:
            similar = []
            if len(self.database[bibcode]['call'].split('B')) > 1:
                for i in self.database:
                    if i != bibcode:
                        if self.database[i]['call'].split('B')[0] == self.database[bibcode]['call'].split('B')[0]:
                            similar.append(self.database[i])
            return self.database[bibcode], similar
        else:
            return None

    def export_bib(self, output_file):
        shutil.copy(self.bib_path, output_file)
