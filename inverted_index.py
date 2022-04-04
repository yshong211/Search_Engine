import json
from bs4 import BeautifulSoup
import os
from pathlib import Path
import glob
from collections import defaultdict
from gensim.models import tfidfmodel
import tokenizer as tknz
import warnings
import nltk
warnings.filterwarnings(action='ignore')

def get_index(lst, word):
    lst_ind = []
    for i in range(len(lst)):
        if lst[i] == word:
            lst_ind.append(i)
    return lst_ind

def getUserInput():
    d = input("Enter the diretory:")
    p = Path(d)
    return p

def loopAllFiles(directory):
    """loop through all csv files in a single director which user enters."""
    extension = 'json'
    os.chdir(directory)
    result = glob.glob('*.{}'.format(extension))
    return result

def walks_dirs(file_path):
    #return the list contains directory
    lst_dir = []
    all_lst = []
    for dirpath, dirname, files in os.walk(file_path):
        lst_dir.append(dirpath)
    for i in lst_dir:
        file_list = loopAllFiles(i)        # error 
        for index in range(len(file_list)):
            file_list[index] = str(i)+"/"+str(file_list[index])
        all_lst += file_list
    return all_lst

def get_content(soup_page, word_count_dict, doc_id):  # Pass in a soup object --> this function will extract the text content in the json and put then into a giant string
    index_dict = defaultdict(list)
    lst_word = []
    lst_word_unweighted = []
    stemmer = nltk.PorterStemmer()
    text_page_bold = ' '
    text_page = ' '
    text_page_h1 = ' '
    text_page_h2 = ' '
    text_page_h3 = ' '
    text_page_title = ' '


    for data in soup_page.find_all(["b",'strong']):
        text_page_bold += data.get_text()
    text_page_bold = text_page_bold.lower()
    tknz_text = tknz.tokenize(text_page_bold)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != ''] * 30
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for data in soup_page.find_all("h1"):
        text_page_h1 += data.get_text()
    text_page_h1 = text_page_h1.lower()
    tknz_text = tknz.tokenize(text_page_h1)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != ''] * 30
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for data in soup_page.find_all("h2"):
        text_page_h2 = data.get_text()
    text_page_h2 = text_page_h2.lower()
    tknz_text = tknz.tokenize(text_page_h2)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != ''] * 20
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for data in soup_page.find_all("h3"):
        text_page_h3 = data.get_text()
    text_page_h3 = text_page_h3.lower()
    tknz_text = tknz.tokenize(text_page_h3)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != ''] * 10
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for data in soup_page.find_all("title"):
        text_page_title = data.get_text()
    text_page_title = text_page_title.lower()
    tknz_text = tknz.tokenize(text_page_title)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != ''] * 100
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for data in soup_page.find_all("p"):
        text_page = data.get_text()
    text_page = text_page.lower()
    tknz_text = tknz.tokenize(text_page)
    lst_word += [stemmer.stem(i) for i in tknz_text if i != '']
    lst_word_unweighted += [stemmer.stem(i) for i in tknz_text if i != '']

    for word in set(lst_word):
        index_dict[word] = get_index(lst_word_unweighted, word)
    lst_return = []
    for word in set(lst_word):
        if word != '':
            lst_return += [[word, lst_word.count(word),index_dict[word]]]
    word_count_dict[doc_id] = len(lst_word)
    return lst_return

def indexing(dict_ind, dict_url, url_num, url, content_list):
    #modify the dict
    dict_url[url_num] = url
    for tple in content_list:
        dict_ind[tple[0]][url_num] =  (tple[1],tple[2])
    
def sortResult(dict1):
    for i in dict1.values():
        i.sort(key=lambda x:x[1], reverse=True)

def dict_to_file(index_dict, count):
    with open('indexes_test_ver2_'+str(count)+'.json', 'w') as j:
        json.dump(index_dict, j)

def run():
    # get all the files in the directory
    word_cout_dict = dict()
    lst_files = walks_dirs(getUserInput())
    # loop through each file and get the content in it
    indexes = defaultdict(dict)
    doc_dict = dict()
    doc_id = 0
    count = 0
    for dir in lst_files[:]:
        with open(dir, 'r') as js:
            html_content = json.load(js)
            try:
                url = html_content['url']
            except KeyError:
                continue
            soup = BeautifulSoup(html_content['content'], 'html.parser', from_encoding=html_content['encoding'])
            content_list = get_content(soup, word_cout_dict, doc_id)
            indexing(indexes, doc_dict, doc_id, url, content_list) # {word: [(url_id, score)]}
            doc_id += 1
            if doc_id%1000 == 0:
                print('Current progress: ', doc_id)
            if doc_id%20000 == 0:
                count += 1
                dict_to_file(indexes, count)
                indexes = defaultdict(dict)
    dict_to_file(indexes, 3)
    print('Finished:', doc_id)
    #sortResult(indexes)
    with open('word_count_page_ver2.json', 'w') as j:
        json.dump(list(word_cout_dict.items()), j)
    with open('doc_id_ver2.json', 'w') as j:
        json.dump(list(doc_dict.items()), j)
    # write the doc_id_dictionary to a json file

if __name__ == '__main__':
    run()

    
