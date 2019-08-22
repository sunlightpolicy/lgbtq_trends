'''
Extract content script
'''
from tqdm import tqdm_notebook as tqdm
from scripts import internetarchive
from nltk.corpus import stopwords
from nltk.collocations import *
from datetime import datetime
from bs4 import BeautifulSoup
import savepagenow
import pandas as pd
import requests
import pickle
import numpy
import nltk
import time
import csv
import re

default_stopwords = set(nltk.corpus.stopwords.words('english'))
all_stopwords = default_stopwords

################################################################################
# Main functions for extracting content ########################################
################################################################################

class Snapshot:
    '''
    Snapshot object that represents a given url at two points of time.
    '''
    def __init__(self, id, url, wayback_url, terms, store_text):
        self.id = id
        self.store_text = store_text
        self._terms = terms
        self.post = {'url': url,
                     'text': None,
                     'results': None,
                     'date': None,
                     'word_count': None}
        self.pre = {'url': wayback_url,
                    'text': None,
                    'results': None,
                    'date': None,
                    'word_count': None}
        self.status = None
        self.exception = None

    def instantiate_object(self, pre_date, post_date):
        '''
        Instantiates the Snapshot object

        Inputs:
            - wayback_date: datetime attribute from wayback object
        '''
        try:
            dict_urls = {'pre': self.pre, 'post': self.post}
            for key, obj in dict_urls.items():
                url = obj['url']
                visible_text = get_visible_txt(url)
                #print(visible_text)
                # initialize list to store term count results
                row = [0] * len(self._terms)
                # count instances on page for each term
                for idx_t, term in enumerate(self._terms):
                    tally, ttal = term_counter(term, visible_text)
                    row[idx_t] = tally
                if self.store_text:
                    obj['text'] = visible_text
                obj['results'] = row
                if key == 'pre':
                    obj['date'] = str(pre_date)
                else:
                    obj['date'] = str(post_date)
                obj['word_count'] = ttal
            self.status = 'succesful'
        except Exception as e:
            self.status = 'failed'
            self.exception = e
            self.pre['results'] = row
            self.post['results'] = row
        self._terms = None #flush variable


def get_output(input_file, output_file, terms, dates_1, dates_2, store_text=True):
    '''
    Counts the ocurrence of terms in a website before and after two specified
    date ranges. Stores information about the url into Snapshot objects. By
    default the visible text is also stored.

    Inputs:
        - input_file (str): path to csv with urls
        - output_file (str): "root name" of produced outputs
        - terms (lst): list of terms to be looked for
        - dates_1 (lst): list of "pre" date range formatted as
            [year_from, month_from, day_from, year_to, month_to, day_to]
        - dates_2 (lst): list of "post" date range formatted as
            [year_from, month_from, day_from, year_to, month_to, day_to]
        - store_text (bool): indicates whether visible text should be stored
            or not

    Outputs:
        - {output_file}_pre.csv: csv file with counts "pre" matrix
        - {output_file}_pre.csv: csv file with counts "post" matrix
        - snapshots.txt: pickle file with Snapshot objects
    '''
    snapshot_lst = [] # saves snapshots to the dump into pickle file
    data = read_csv(input_file)
    # set up columns for csv output
    col_names = ['url', 'date', 'wayback_url'] + terms
    # list of lists to store heterogenous data
    matrix_pre = [[] for i in range(len(data))]
    matrix_post = [[] for i in range(len(data))] # urls restricted by matrix pre

    len_data = len(data)
    idx_e = 0
    for elmt in tqdm(data, desc='progress: '):
        current_url = elmt[0] # grab url
        #print(current_url)
        try:
            with internetarchive.WaybackClient() as client:
                # save current state as you go
                archive_url, captured = savepagenow.capture_or_cache(current_url)
                #print(archive_url)
                # fetch all wayback instances within the date-ranges
                pre_dump = client.list_versions(current_url,
                                            from_date=datetime(dates_1[0],
                                                               dates_1[1],
                                                               dates_1[2]),
                                            to_date=datetime(dates_1[3],
                                                             dates_1[4],
                                                             dates_1[5]))
                post_dump = client.list_versions(current_url,
                                            from_date=datetime(dates_2[0],
                                                               dates_2[1],
                                                               dates_2[2]),
                                            to_date=datetime(dates_2[3],
                                                             dates_2[4],
                                                             dates_2[5]))
                try:
                    status_codes = ['200', '-'] #, '301'
                    post_versions = list(post_dump)[::-1]
                    for i_post, current_version in enumerate(post_versions):
                        # get most recent viable version of post
                        if any(current_version.status_code == code for code in status_codes):
                            current_url = current_version.raw_url #switch to IAWM version
                            pre_versions = list(pre_dump)[::-1]
                            for i_pre, latest_version in enumerate(pre_versions):
                                # get most recent viable version of pre
                                if any(latest_version.status_code == code for code in status_codes):
                                    # found the latest viable version for both timeframes
                                    wayback_url = latest_version.raw_url # get the archive's url
                                    snapshot = Snapshot(idx_e + 1, current_url, wayback_url, terms, store_text)
                                    snapshot.instantiate_object(latest_version.date, current_version.date)
                                    matrix_post[idx_e] = snapshot.post['results']
                                    matrix_pre[idx_e] = snapshot.pre['results']
                                    break
                                elif i_pre == len(pre_versions) - 1:
                                    # not able to retrieve both viable versions succesfully
                                    snapshot = Snapshot(idx_e + 1, current_url, None, terms, store_text)
                                    snapshot.status = 'failed'
                                    snapshot.exception = latest_version.status_code
                                    row = [None] * len(terms) # update matrix with Nones
                                    matrix_pre[idx_e] = row
                                    matrix_post[idx_e] = row
                                else:
                                    # still searching pre version
                                    continue
                            break
                        elif i_post == len(pre_versions) - 1:
                            # unsuccesful search of viable post
                            snapshot = Snapshot(idx_e + 1, current_url, None, terms, store_text)
                            snapshot.status = 'failed'
                            snapshot.exception = latest_version.status_code
                            row = [None] * len(terms) # update matrix with Nones
                            matrix_pre[idx_e] = row
                            matrix_post[idx_e] = row
                        else:
                            # still searching post version
                            continue
                        break
                except Exception as e: # unparseable format
                    snapshot = Snapshot(idx_e + 1, current_url, None, terms, store_text)
                    snapshot.status = 'failed'
                    snapshot.exception = e
                    row = [None] * len(terms) # update matrix with Nones
                    matrix_pre[idx_e] = row
                    matrix_post[idx_e] = row
        except Exception as e: # no wayback url
            snapshot = Snapshot(idx_e + 1, current_url, None, terms, store_text)
            snapshot.status = 'failed'
            snapshot.exception = e
            row = [None] * len(terms) # update matrix with Nones
            matrix_pre[idx_e] = row
            matrix_post[idx_e] = row

        snapshot_lst.append(snapshot)
        idx_e += 1
        #print(idx_e, len(snapshot_lst), current_url)

    save_csv(matrix_pre, output_file,'_pre')
    save_csv(matrix_post, output_file,'_post')
    with open('outputs/snapshots_{}.txt'.format(output_file), "wb") as fp:
        pickle.dump(snapshot_lst, fp) #pickling

################################################################################
# Get links from usa.gov #######################################################
################################################################################

def gen_usagovsearch(terms, depth):
    '''
    Generates a csv file with a list of search engine links given a list of
    search terms.

    Inputs:
        - terms (lst): a list of string search terms
        - depth (int): number of pages from the search engine we want to generate

    Outputs: a list of search engine urls as well as the same list as a csv
    '''
    urls = []
    for term in terms:
        if isinstance(term, list):
            search_str = ['+'.join(map(str, term))][0]
        else:
            search_str = term
        initial_search = 'https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=usagov&query={}'.format(
                          search_str)
        urls.append(initial_search)
        for i in range(depth)[1:]:
            page_num = i + 1
            next_search = 'https://search.usa.gov/search?affiliate=usagov&page={}&query={}&utf8=%E2%9C%93'.format(
            page_num, search_str)
            urls.append(next_search)

    df = pd.DataFrame(urls, columns=["urls"])
    df.to_csv('inputs/usagovsearch_urls.csv', index=False)

    return urls

def get_hrefs(urls):
    '''
    Gets the urls from a given usa.gov search engine page and restricts them to
    federal government webpages to the extent possible, excluding some formats
    like pdf, doc, ppt.

    Inputs:
        - urls (lst): list of strings

    Outputs:
        - url_set (set): a set of unique urls
        - exceptions (lst): a list of any encountered exceptions
    '''
    url_set = set()
    exceptions = []
    for url in urls:
        try:
            with internetarchive.WaybackClient() as client:
                # lookup the versions to scrape them because direct scrape fails
                dump = client.list_versions(url,
                                            from_date=datetime(2019,
                                                               8,
                                                               1),
                                            to_date=datetime(2019,
                                                             8,
                                                             8))
                latest_version = list(dump)[::-1][0]
                wayback_url = latest_version.raw_url
                #print(wayback_url)
                wayback_date = latest_version.date
                contents = requests.get(wayback_url).content.decode()
                soup = BeautifulSoup(contents, 'lxml')
                soup = soup.find('div', {'id': 'results'})
                for a in soup.find_all('a', href=True):
                    link = a['href'].lower()
                    #print(link)
                    states = ['alabama.', 'alaska.', 'az.', 'arkansas.', 'ca.',
                              'colorado.', 'ct.', 'delaware.', 'myflorida.',
                              'georgia.', 'hawaii.', 'illinois','in.', 'iowa.',
                              'kansas.', 'kentucky.', 'lousiana.', 'maine.',
                              'maryland.', 'mass.', 'michigan.', 'mn.', 'ms.',
                              'mo.', 'mt.', 'nebraska.', 'nv.', 'nh.', 'nj.',
                              'ny.', 'nc.', 'nd.', 'ohio.', 'ok.', 'oregon.',
                              'pa.', 'ri.', 'sc.', 'sd.', 'tn.', 'texas.',
                              'utah.', 'vermont.', 'virginia.', 'wa.', 'wv.',
                              'wisconsin.', 'wyo.', '.wi.']
                    other = ['nyc.', 'ma.', 'tx.', 'county', 'city', '.house.',
                            'smithsonian', 'usembassy', 'longbeach', '.dc.',
                            'phila', 'whitehouse', 'seattle', '.loc.gov', 'fmcs',
                            'cabq', 'atlantaga', 'alexandriava', 'loudoun',
                            'fortlauderdale', 'nysed', 'nycourts']
                    not_accepted = ['.pdf', '.doc', '.docx', '.rtf',
                                    'news', 'blog', 'espanol', 'spanish'
                                    '.pptx'] + states + other
                    if not any(element in link for element in not_accepted):
                        if '.gov' in link: #only .gov links
                            #print(wayback_date)
                            url_set.add(link) #get rid of web.archive part
        except Exception as e:
            #print(e, url)
            exceptions.append(url)

    return url_set, exceptions

################################################################################
# HUD analysis functions #######################################################
################################################################################

from selenium import webdriver
from dateutil.parser import parse
#import internetarchive
import requests
from os import path
import csv
import os
import shutil
from urllib.parse import urljoin
import savepagenow

def open_chrome(wayback_url, driver_path):
    '''
    '''
    browser = webdriver.Chrome(executable_path=driver_path)
    browser.get(wayback_url)
    return browser


def get_urls(browser, analysis_from, analysis_to, output_name):
    # take all valid urls that existed
    stored_urls = []
    try:
        analysis_from = parse(analysis_from)
        analysis_to = parse(analysis_to)
        # get number of pages to go through
        page_num = int(browser.find_element_by_xpath(
                        '//a[@class="paginate_button " and @data-dt-idx="7"]').text)
        #print(page_num)
        for page in tqdm(range(page_num), desc='progress: '):
        #for page in range(page_num):
            #print('***** Working on page ', page)
            time.sleep(1)
            links = browser.find_elements_by_xpath('//tr[@role="row"]//td//a[@href]')
            type = browser.find_elements_by_xpath('//tr[@role="row"]//td[@class=" mimetype"]')
            dates_from = browser.find_elements_by_xpath('//tr[@role="row"]//td[@class=" dateFrom"]')
            dates_to = browser.find_elements_by_xpath('//tr[@role="row"]//td[@class=" dateTo"]')
            if len(links) == len(dates_from) == len(dates_to) == len(type):
                for i, link in enumerate(links):
                    current_type = type[i]
                    current_url = link.get_attribute('href')
                    if 'text/html' in current_type.text:
                        #print('got product')
                        date_from = parse(dates_from[i].text)
                        date_to = parse(dates_to[i].text)
                        # make sure wayback snapshots are within range
                        if not((date_to < analysis_from) or (date_from > analysis_to)):
                            #print('Not valid ', current_url)
                        #else:
                            #print('Success from ', date_from, 'to ', date_to)
                            stored_urls.append([current_url, date_from, date_to])
                if page != page_num - 1:
                    button = browser.find_element_by_xpath(
                            '//a[@class="paginate_button next" and @id="resultsUrl_next"]')
            if page != page_num - 1:
                button.click()
    except Exception as e:
        print(e)

    with open(output_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stored_urls)

    return stored_urls

    stored_copy = stored_urls[:]
    len('https://web.archive.org/web/*/')
    for row in stored_copy:
        row[0] = row[0][30:]

################################################################################
# Helper functions #############################################################
################################################################################

def save_csv(matrix, output_file, name):
    '''
    Saves matrix into csv file
    '''
    with open('outputs/' + output_file + name + '.csv', "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(matrix)

def read_csv(input_file):
    '''
    Reads in a simple csv with a list of links
    '''
    with open(input_file) as csvfile:
        # read and grab the input data
        read = csv.reader(csvfile)
        data = list(read)
        csvfile.close()

        return data

def term_counter(term, visible_text):
    '''
    Counts terms of varying length

    Inputs:
        - term (str or lst of str):

    Outputs:
        - tally (int): number of times that the term appears in visible text
        - ttal_words (int): number of total words in visible text

    Attributions: based on EDGI's code
    '''
    tally = 0
    ttal_words = 0
    if not isinstance(term, list): #put single word strings into a list
        term = [term]
    term = [re.sub(r'[^\w\s]', '', x) for x in term]
    length = len(term)
    for section in visible_text:
        #print(visible_text)
        tokens = nltk.word_tokenize(section) # tokenize
        tokens = [x.lower() for x in tokens] # convert to lowercase
        tokens = [re.sub(r'[^\w\s]', '', x) for x in tokens] # get rid of punctuation
        tokens = [x for x in tokens if x != ''] # get rid of ''
        grams = nltk.ngrams(tokens, 1)
        all_words = [item[0] for item in grams]
        ttal_words += len(all_words)
        if length >= 1:
            grams = nltk.ngrams(tokens, length) # get ngrams
        fdist = nltk.FreqDist(grams) # get frequency distribution
        key = tuple([term[i].lower() for i in range(length)])
        tally += fdist[key]

    return tally, ttal_words

def get_visible_txt(url):
    '''
    Gets visible text content from different federal government department
    subdomains

    Inputs:
        - url (str): a url from a federal government department

    Outputs:
        - body (lst): list of strings
    '''
    contents = requests.get(url).content.decode()
    contents = BeautifulSoup(contents, 'lxml')
    body = contents.find('body')

    tags = ['header', 'nav', 'script', 'style', 'footer', 'meta', '[document]', 'title']

    id_terms = ['footer', 'breadcrumb', 'banner', 'sidebar', 'ribbon', 'navigation',
                'skipnutch', 'lastmodified', 'head', 'menu', 'search', 'social',
                'language', 'branding', 'table-of-contents']
    class_terms = ['footer', 'breadcrumb', 'sidebar', 'ribbon', 'social', 'media',
                   'back-to-top', 'lastmodified', 'addthis', 'global-nav',
                   'slideout', 'connect clearfix', 'modal fade', 'csshide']
    other_terms = ['[role*="navigation" i]', '[role*="banner" i]', '#OMh_Menu_pnlMenu',
                '[role*="presentation"]', '[title*="go to top"]',
                '[class*="sr-only ng-binding ng-scope"]']
    if 'peacecorps' in url:
        class_terms = [x for x in class_terms if x not in ['sidebar']]
    if 'minorityhealth' in url:
        id_terms = [x for x in id_terms if x not in ['head', 'menu']]
    if 'travel.state.gov' in url:
        class_terms.extend(['nav', 'bottom'])
    if '.va.gov' in url:
        id_terms.extend(['leftNavContainer'])
    if 'bls.gov' in url:
        id_terms.extend(['main-nav', 'secondary-nav-td', 'quicklinks'])
    if 'healthypeople.gov' in url:
        id_terms = [x for x in id_terms if x not in ['head']]
    if 'ncbi.nlm.nih' in url:
        class_terms.extend(['search', 'four_col col last'])
        #id_terms.extend(['main-nav', 'secondary-nav-td', 'quicklinks'])

    ids = ['[id*="{}" i]'.format(x) for x in id_terms]
    classes = ['[class*="{}" i]'.format(x) for x in class_terms]
    del_lst = tags + ids + classes + other_terms
    tags = ['nav']

    for s in del_lst:
        d = [s.extract() for s in body.select(s)]
    del d

    body = [text for text in body.stripped_strings]

    return body
