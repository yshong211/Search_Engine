from collections import defaultdict
import time
import math
import json
from sys import path_importer_cache, stderr
import nltk
import re
from urllib.parse import urlparse
from nltk.corpus import stopwords
class Search_Engine():
    def __init__(self):
        self.dict_index = dict()
        self.query_list = []
        self.load_index()
        self.load_doc_id_dict()
        self.load_word_count_dict()
    

    def load_index(self) -> dict: # load the index into a dict
        if self.query_list == []:
            for i in range(26):
                with open('index_'+str(i)+'.json', 'r') as j:
                        temp_dict = json.load(j)
                self.dict_index.update(temp_dict)
        else:
            for word in self.query_list:
                if word not in self.dict_index:
                    if ord(word[0]) >= 48 and ord(word[0]) <= 57:
                        # number
                        with open('index_number.json', 'r') as j:
                            temp_dict = json.load(j)
                        self.dict_index[word] = temp_dict[word]
                        del temp_dict

                    elif ord(word[0]) >= 97 and ord(word[0]) <= 97+26:
                        with open('index_'+str(ord(word[0])-97)+'.json', 'r') as j:
                            temp_dict = json.load(j)
                        self.dict_index.update(temp_dict)
                        del temp_dict


    def load_doc_id_dict(self) -> dict:
        with open('doc_id_ver2.json', 'r') as d:
            self.doc_id_dict = dict(json.load(d))


    def load_word_count_dict(self):
        with open('word_count_page_ver2.json') as d:
            self.word_count_dict = dict(json.load(d))


    def get_url(self,doc_id) -> str: # pass in a doc_id and give you the corresponding url
        #print("    doc_id: ", doc_id)
        return self.doc_id_dict[doc_id]


    def get_query(self): # split and stem the query into a list of string
        query = input("Search(enter nothing to quit): ")
        if query == '':
            exit()
        list_query = re.split(pattern=r'\W+', string=query)
        stemmer = nltk.PorterStemmer()                                                          #jay's get_query
        self.query_list = [stemmer.stem(token) for token in list_query if token != '']
        for i in self.query_list:
            if 'and' == i:  # Dealing with the  and  query, not including 'and' as a query
                self.query_list.remove(i)
        

    def get_id2ind(self,lst_ovlp):
        dict_id2ind = dict()
        for id in lst_ovlp:
            lst_ind = []
            for q in self.query_list:
                lst_ind.append(self.dict_index[q][str(id)][1]) # this will get the index list in the posting
            dict_id2ind[id] = lst_ind
        return dict_id2ind


    def get_phrase_count(self,dict_id2ind):
        phrase_count_dict = dict()
        for k in dict_id2ind: # k is the doc id
            phrase_count = len(dict_id2ind[k][0])
            for i in range(len(dict_id2ind[k])):
                if i == 0:
                    word_ind = dict_id2ind[k][0]
                else:
                    for ind in word_ind:
                        if ind+1 not in dict_id2ind[k][i]:
                            phrase_count -= 1
                            break
            phrase_count_dict[k] = phrase_count
        return phrase_count_dict


    def filter_url(self,doc_id_lst):
        path_count = defaultdict(int)
        url_set = set()
        lst_dup = []
        top_url = ''
        for doc_id in doc_id_lst:
            p = urlparse(self.doc_id_dict[doc_id])
            if p.netloc+p.path not in url_set:
                url_str = p.netloc+p.path
                url_str = '/'.join(url_str.split('/')[:2])
                path_count[url_str] += 1
                url_set.add(p.netloc+p.path)
            else:
                lst_dup.append(doc_id)
        find_top = sorted([url for url in path_count.keys()], key= lambda x: path_count[x], reverse=True)
        if len(find_top) != 0:
            top_url = find_top[0] +'/'
        return top_url , [id for id in doc_id_lst if id not in lst_dup + ['https://'+top_url,'http://'+top_url]]
                

    def normalize_vector(self, v):
        size_of_v = math.sqrt(sum([i**2 for i in v]))
        return [i/size_of_v for i in v]


    def result_sorting(self,phrase_count) -> list:
        
        query_document_tf_idf = {}
        for doc_id in phrase_count:
            query_tf_idf_vector = []
            doc_tf_vector = []
            for w in self.query_list:

                #query tf idf
                query_term_freq = 1 + math.log(self.query_list.count(w), 2)
                i_doc_freq = math.log( 55394 / len(list(self.dict_index[w].keys())))
                query_tf_idf = query_term_freq * i_doc_freq
                #doc tf idf
                #print(self.dict_index[w])
                #'55283': [161, [4, 10, 27, 40]]
                doc_term_freq = 1 + math.log(self.dict_index[w][str(doc_id)][0], 2)

                #create vector
                doc_tf_vector.append(doc_term_freq)
                query_tf_idf_vector.append(query_tf_idf)
                #end for
            # create a dict, which its values are a tuple of two vector. query v on index 0 and doc v on index 1
            
            query_document_tf_idf[doc_id] =  (self.normalize_vector(query_tf_idf_vector), self.normalize_vector(doc_tf_vector))
            
        cosine_score_dict = self.calculate_cosine_similarity(query_document_tf_idf)
        
        return sorted([doc_id for doc_id in cosine_score_dict], key= lambda x: cosine_score_dict[x], reverse=True)


    def calculate_cosine_similarity(self, query_doc_tf_idf_dict):
        self.cos_score_dict = dict()
        for doc_id, qd_vector in query_doc_tf_idf_dict.items():
            cos_score = sum(qd_vector[0][i]+qd_vector[1][i] for i in range(len(qd_vector[0])))
            self.cos_score_dict[doc_id] = cos_score
        return self.cos_score_dict


    def searching(self): # this is where the actual searching is happening
        start_time = time.time()
        self.load_index()
        lst_all_words = []
        search_result = [] # list of doc ids
        # search machine learning
        # step1. find list of doc_id that contains both machine and learning.
        # step2. for each doc_id, for the ind_list in the index, count how many machine ind+1 is in learning ind list.
        # step3. based on the count you got, calculate tf-idf score.
        for q in self.query_list[:]:
            if q in self.dict_index:
                lst_all_words.append([int(doc_id) for doc_id in self.dict_index[q].keys()])
            else:
                self.query_list.remove(q)
        if len(self.query_list) == 0:
            print('No record')
            return
        lst_ovlp = lst_all_words[0]
        for i in range(len(lst_all_words)):
            lst_ovlp = list(set(lst_ovlp) & set(lst_all_words[i]))
        # we now have the overlapping doc_ids list
        #step2.
        dict_id2ind = self.get_id2ind(lst_ovlp)
        phrase_count = self.get_phrase_count(dict_id2ind)
        sorting_timer = time.time()
        search_result = self.result_sorting(phrase_count)
        print('sorting used', time.time()-sorting_timer,'to execute.')
        top_url, search_result = self.filter_url(search_result)
        if search_result == []:
            self.query_list = self.query_list[0]
            return self.searching()
        if top_url != '':
            print('Search found @: https://'+top_url)
        for doc_id in search_result[:10]:
            print('Search found @:', self.get_url(doc_id))
            #print("    with score:", self.cos_score_dict[doc_id])
        
        print('Search used', time.time()-start_time,'to execute.')
    

    def run(self):
        while True:
            self.get_query()
            self.searching()


if __name__ == '__main__':
    print('--------\nSearch Engine\n--------\n')
    searchEngine = Search_Engine()
    searchEngine.run()

# Structure of the index posting:
            # {token: [doc_id, td_idf_scoring]}

            #                           I   eat   apple
            #document tf_idf : doc1:   0.3  0.1   0.2
            # q tf_idf                 0.3  0.3   0.3

