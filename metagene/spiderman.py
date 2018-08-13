'''
主程序

Created on 2018/08/13.
'''

__author__ = 'Feng Xie'

from downloader import DiseasesDownloader
from bs4 import BeautifulSoup
import logging
from threading import Thread
import time
from queue import Queue
from multiprocessing import Pool, Process
from settings import LOGGER

# from pipelines import Pipelines as db

# base_url = 'http://www.hiyd.com'
logger = logging.getLogger(LOGGER)

class Spider:

    def __init__(self):
        logger.info('[spider opened]')

    def run(self):
        disease = DiseasesDownloader()
        disease_id_list = disease.get_diseases_id()
        base_urls = {
            'disease': 'http://www.metagene.de/appl/diseases.prg?act=show&id=',
            'symptom': 'http://www.metagene.de/appl/symptoms.prg?act=getGridData&id_d=',
            'normal': 'http://www.metagene.de/appl/normal.prg?act=getData&id_d=',
            'lab': 'http://www.metagene.de/appl/lab.prg?act=getGridData&id_d=',
            'literature': 'http://www.metagene.de/appl/authors.prg?act=getGridData&withLink=1&id_d='
        }
        # 爬取疾病的进程必须先进行，因为其他爬虫需要以疾病 id 作为外键
        priority_task = Process(target=disease.schedule, args=(disease_id_list, base_urls['disease'], 'disease'))
        priority_task.start()
        priority_task.join()
        # 理论上，以下的爬取symptom、lab、normal_specimens、literature四个进程可以同时进行
        # 但过程中可能会发生一些不可预知的错误，而且去重比较麻烦，所以一个一个跑比较保险
        p = Pool(4)
        # p.apply_async(disease.schedule, args=(disease_id_list, base_urls['symptom'], 'symptom'))
        # p.apply_async(disease.schedule, args=(disease_id_list, base_urls['normal'], 'normal'))
        # p.apply_async(disease.schedule, args=(disease_id_list, base_urls['lab'], 'lab'))
        p.apply_async(disease.schedule, args=(disease_id_list, base_urls['literature'], 'literature'))
        p.close()
        p.join()


if __name__ == '__main__':
    Spider().run()
    
        
