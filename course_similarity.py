#!/usr/bin/env python
# coding=utf-8

import json
import nltk
from nltk.stem import snowball
from gensim import corpora,models,similarities
import re
import string
import glob


def load_stopword():
    f = open("../gensim_test/stop_words_english_en.txt","r")
    words = f.read()
    stop_words = set(words.split("\n"))
    return stop_words

def course_prerequisite_parse(course_prereq):
    '''抽取预修课程中隐藏的预修课程id'''
    course_prereq_id = []
    if len(course_prereq) > 0:
        pattern = re.compile(r".*\..+")
        course_prereq_id = []
        for i in course_prereq:
            pre_list = i.split()
            for word in pre_list:
                if pattern.match(word):
                    word = word.lower().replace(".","")
                    word = word.replace("(","")
                    word = word.replace(")","")
                    course_prereq_id.append(word)
        return course_prereq_id
    else:
        return None
            

def course_desc_preprocess(course_desc):
    if len(course_desc)>0:
        pattern = re.compile(r"\d+")
        st = snowball.EnglishStemmer()
        stop_words = load_stopword()
        course_desc_words = []
        for i in course_desc:
            tokens = nltk.word_tokenize(i.lower().strip())
            course_desc_words.extend(tokens)
        course_desc_words = [word for word in course_desc_words if word not in stop_words and word not in string.punctuation and not pattern.match(word)]
        for num,word in enumerate(course_desc_words):
            course_desc_words[num] = st.stem(word)
        return course_desc_words
    else:
        return None


def course_preprocess(filepath,stop_words):
    f = open(filepath,"r")
    material = f.read()
    f.close()
    course_material =  json.loads(material)
    course = {}
    course["name"] = course_material["course_name"]
    course["id"] = course_material["course_id"].lower()
    course["prerequisite"] = course_prerequisite_parse(course_material["course_prerequisites"])
    course["desc"] = course_desc_preprocess(course_material["course_description"])
    course["sim"] ={}
    if course["desc"] is None:
        return None
    else:
        return course

def wordDict_courselist_courseMatrix_generation():
    filepath = glob.glob("./mit_course/course_corpus/*.json")
    stop_words = load_stopword()
    course_matrix = []
    course_list = []
    for file in filepath:
        if course_preprocess(file,stop_words) is None:
            continue
        else:
            course = course_preprocess(file,stop_words)
            course_matrix.append(course["desc"])
            course_list.append(course)
    word_dict = corpora.Dictionary(course_matrix)
    course_matrix = [word_dict.doc2bow(text) for text in course_matrix]
    return word_dict,course_list,course_matrix

if __name__ == "__main__":
    try:
        word_dict = corpora.Dictionary.load("./course_word_dictionary.dict")
        f = open("./course_list.json").read()
        course_list = json.loads(f)
        f.close()
        course_matrix = corpora.MmCorpus("./course_matrix.mm")
    except:
        word_dict,course_list,course_matrix = wordDict_courselist_courseMatrix_generation()
        corpora.MmCorpus.serialize('./course_matrix.mm',course_matrix)
        word_dict.save("./course_word_dictionary.dict")
        f = open("./course_list.json","w")
        f.write(json.dumps(course_list))
        f.close()
    
    try:
        course_tfidf = corpora.MmCorpus("./course_tfidf.mm")
    except:
        tfidf = models.TfidfModel(course_matrix)
        course_tfidf = tfidf[course_matrix]
        corpora.MmCorpus.serialize("./course_tfidf.mm",course_tfidf)

    try:
        lda = models.LdaModel.load("./ldamodel.lda")
    except:
        lda = models.LdaModel(corpus=course_tfidf,num_topics=500,id2word=word_dict,iterations=100)
        #模型的收敛型太差，基本每次训练都能找到不一样的最优点，可能是语料量和处理方法都有问题。 
        lda.save("./ldamodel.lda")


    try:
        lda_index = similarities.MatrixSimilarity.load("./course_lda.index")
    except:
        lda_index = similarities.MatrixSimilarity(lda[course_tfidf])
        lda_index.save("./course_lda.index")

    sum_sim = 0
    course_lda = lda[course_tfidf]
    for num,course_lda_vec in enumerate(course_lda):    
        sims = lda_index[course_lda_vec]
        sims_sorted = sorted(enumerate(sims),key=lambda item:-item[1])
        for sim in sims_sorted:
            if sim[1]>0.9 and num != sim[0]:
                print(num,sim[0],sim[1])  #最多只能打印到小数点后6位
                course_list[num]["sim"][str(sim[0])] =  float('%.10f'%sim[1])   
                #暂时不知道为什么，不用float函数规范一下位数，再利用json转存时，会出现type_error
                sum_sim += 1
            else:
                break
    
    print(len(word_dict.keys()))
    print(sum_sim/len(course_list))
    course_list_file = open("course_list.json","w")
    json.dump(course_list,course_list_file,skipkeys=True)
    course_list_file.close()


    



    
    

