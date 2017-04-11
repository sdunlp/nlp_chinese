# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from snownlp import normal
from snownlp import seg
from snownlp.summary import textrank
from snownlp import SnowNLP
import sys
import os
import os.path
import json

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def getListFiles(fold):
    ret = []
    a = []
    for root, dirs, files in os.walk(fold):
        for filespath in files:
            ret.append(os.path.join(root, filespath))
            a.append(filespath)
    return a


def getJson(fold, filename):
    count = 0
    cotent = u''
    title = ''
    time = ''
    abstract = ''
    path = fold + '/' + filename
    # ========================================
    #    读取文件的时间、标题、内容
    # ========================================
    for line in open(path, 'r'):
        if (count == 0):
            title = line.replace("标题:", "", 1)
            count += 1
            # print (title)
            continue
        if (count == 1):
            time = line.replace("时间:", "", 1)
            count += 1
            # print (time)
            continue
        if (count > 1):
            count += 1
            cotent += line
            # print (line)
    cotent = cotent.replace("内容:", "", 1)
    # print (cotent)

    # ========================================
    #      生成摘要
    # =======================================


    t = normal.zh2hans(cotent)
    sents = normal.get_sentences(t)
    doc = []
    for sent in sents:
        words = seg.seg(sent)
        words = normal.filter_stop(words)
        doc.append(words)
    rank = textrank.TextRank(doc)
    rank.solve()
    for index in rank.top_index(5):
        abstract = abstract + sents[index] + ' '
    keyword_rank = textrank.KeywordTextRank(doc)
    keyword_rank.solve()
    word0 = {}
    word1 = {}
    word2 = {}
    word3 = {}
    word4 = {}
    wordcount = 0
    for w in keyword_rank.top_index(5):
        if wordcount == 0:
            word0["word"] = w
            word0["frequency"] = cotent.count(w)

        if wordcount == 1:
            word1["word"] = w
            word1["frequency"] = cotent.count(w)
        if wordcount == 2:
            word2["word"] = w
            word2["frequency"] = cotent.count(w)
        if wordcount == 3:
            word3["word"] = w
            word3["frequency"] = cotent.count(w)
        if wordcount == 4:
            word4["word"] = w
            word4["frequency"] = cotent.count(w)
        wordcount += 1

    s = SnowNLP(cotent)
    score = (s.sentiments - 0.5) * 2  # -1-1规范化

    keywords = [word0, word1, word2, word3, word4]
    result = {}
    result["code"] = 1
    result["message"] = "sucess"
    result["tilte"] = title.strip()
    result["time"] = time.strip()
    result['abstract'] = abstract
    result['sentiment'] = score
    result["keywords"] = keywords

    return result


if __name__ == '__main__':
    fold = str(sys.argv[1])
    result = []
    ret = getListFiles(fold);
    data = {}
    for each in ret:
        result = getJson(fold, each)
        data[each] = result

    jsonStr = json.dumps(data, ensure_ascii=False)
    print(jsonStr)