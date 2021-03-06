# -*- coding : utf-8 -*-
import jieba
import json
import re

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import os
import logging

logging.basicConfig(level = logging.INFO,filename='all.log',format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
http_ignore = re.compile(r'[http|https]*:?//[a-zA-Z0-9.?/&=:]*', re.S)
parent_ignore = re.compile(u"\\(.*?\\)|\\{.*?\\}|\\[.*?\\]")
special_ignore = re.compile(u"[^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a]")


class MyWordCloud:
    def __init__(self, number):
        self.number = number

    def word_seg(self, path_corpus, path_seg):
        with open(path_corpus, 'r', encoding='utf-8') as rf, open(path_seg, 'a', encoding='utf-8') as wf:
            data = json.load(rf)
            for d in data["weibo"]:
                content1 = re.sub(http_ignore, '', d['content'])
                content2 = re.sub(parent_ignore, '', content1)
                content3 = re.sub(special_ignore, '', content2)
                d['content'] = content3
                print(d['content'])
                word_segs = jieba.cut(d['content'])
                words = list()
                for w in word_segs:
                    words.append(w)
                d["content"] = ' '.join(words)
            #print(data)
            json.dump(data, wf, ensure_ascii=False, indent=8)

    def word_count(self, path_word_seg, path_word_items, path_stop):
        with open(path_word_seg, 'r', encoding='utf-8') as rf, open(path_word_items, 'a', encoding='utf-8') as wf:
            data = json.load(rf)
            print(data)
            word_freq = dict()
            with open(path_stop, 'r', encoding='utf-8') as temp:
                stop_words = temp.read()
            for d in data["weibo"]:
                wb = d['content'].split(' ')
                for w in wb:
                    if w not in stop_words:
                        word_freq[w] = word_freq.get(w, 0) + 1
            word_items = list(word_freq.items())
            word_items.sort(key=lambda x: x[1], reverse=True)
            # items = dict(word_items)
            # print(word_items)
            json.dump(dict(word_items), wf, ensure_ascii=False, indent=8)

    def word_str(self, path_word):
        with open(path_word, 'r', encoding='utf-8') as rf:
            data = json.load(rf)
            print(data)
        word_items = list(data.items())
        print(word_items)
        word_list = list()
        for i in range(min(self.number, len(word_items))):
            word, count = word_items[i]
            print("{0:<10}{1:<5}".format(word, count))
            word_list.append(word)
        word_str = ' '.join(word_list)
        return word_str

    def create_word_cloud(self, word_str, path_wordcloud, name):
        cloud_mask = np.array(Image.open("./background.jpg"))  # ?????????????????????????????????????????????
        wc = WordCloud(
            background_color="black",  # ????????????
            mask=cloud_mask,  # ?????????cloud_mask
            max_words=self.number,  # ??????????????????
            font_path='simsun.ttf',  # ??????font??????simsun.tff???????????????????????????
            height=1200,  # ????????????
            width=1600,  # ????????????
            max_font_size=1000,  # ???????????????
            random_state=1000,  # ??????????????????????????????????????????????????????
        )

        myword = wc.generate(word_str)  # ??? wl????????? ????????????
        # ???????????????
        # plt.figure(num=name+'??????????????????')
        # plt.imshow(myword)
        # plt.axis("off")
        # plt.show()
        wc.to_file(path_wordcloud)  # ???????????????????????????????????????py?????????????????????

if __name__ == '__main__':
    # corpus = "./1947487982.json"
    # seg = "./word_seg_1947487982.json"
    #
    # word_freq = "./word_freq_1947487982.json"
    # path_jpg = './1947487982.jpg'
    number = 100
    myword = MyWordCloud(number)
    # ??????weibo?????????????????????????????????????????????????????????json?????????'
    path = './../weiboRecommend/weiboSpider/2019??????2020????????????'
    stop = "./stop_words.txt"
    user_id_list = './test.txt'
    id_list = './todo_id2.txt'
    try:
        with open(user_id_list, 'r', encoding='utf-8') as rf:
            logger.info(u"????????????ids...")
            data = rf.readlines()
            for line in data:
                line = line.strip('\n')
                name = line.split(' ')[1]
                id = line.split(' ')[0]
                corpus = path + '/' + name + '/' + id + '.json'
                #print(corpus)
                if os.path.exists(corpus):
                    logger.info(u"????????????%s?????????" % name)
                    seg = corpus[:-5] + '_seg3.json'
                    word_freq = corpus[:-5] + '_freq3.json'
                    path_jpg = corpus[:-5] + '_??????3.jpg'
                    myword.word_seg(corpus, seg)
                    myword.word_count(seg, word_freq, stop)
                    myword.create_word_cloud(myword.word_str(word_freq), path_jpg, name)
                else:
                    with open(id_list, 'a', encoding='utf-8') as wf:
                        logger.info(u'%s?????????' % name)
                        wf.write(line)
    except Exception as e:
        logger.exception(e)

