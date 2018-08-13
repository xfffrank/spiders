'''
下载器
'''
import requests
import random
import logging
import time
import re
from build_ip_pool import GetIp
from json.decoder import JSONDecodeError
import json
import re
from bs4 import BeautifulSoup
from bs4.element import Tag

from pipelines import MySQLPipelines as mysql
from settings import LOGGER
# from pipelines import MongoPipelines as mongo

from queue import Queue
from threading import Thread
from multiprocessing import Lock

logger = logging.getLogger(LOGGER)
logger.setLevel(logging.DEBUG)  # 设置控制台的日志输出级别
ch = logging.StreamHandler()
fh = logging.FileHandler('log/download.log', encoding='utf-8', mode='a')  # w 覆盖原文件，a 追加
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
ch.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)

class Downloader:

    def __init__(self):
        # lock.acquire()
        try:
            with open('proxies.txt') as f:
                self.proxy_list = f.readlines()
        except:
            logger.info('-'*10 + '代理文件不存在，重新下载代理' + '-'*10)
            g = GetIp(verify_site='http://www.metagene.de/appl/diseases.prg?act=show&id=458')
            g.get_proxy_ip()
            g.verify_proxies()
            with open('proxies.txt', 'w') as f:
                for proxy in g.proxy_list:
                    f.write(proxy + '\n')
                self.proxy_list = g.proxy_list
        # finally:
        #     lock.release()
        self.proxy = random.choice(self.proxy_list).strip()
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
            "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

    def get(self, url):
        headers = {
            'User-Agent': random.choice(self.user_agent_list),
        }
        protocol = 'https' if 'https' in self.proxy else 'http'
        proxies = {
            protocol: self.proxy
        }
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        except Exception as e:
            logger.info(url + '下载出错，原因：' + str(e))
            logger.debug('[requests]正在更换代理ip...')
            self.proxy = random.choice(self.proxy_list).strip()
            time.sleep(1)
            return self.get(url)
        else:
            return response.text


class DiseasesDownloader(Downloader):

    def __init__(self):
        super().__init__()
        self.download_func = {    # 下载函数字典
            'disease': self.download_disease_info,
            'symptom': self.download_symptom_info,
            'lab': self.download_lab_info,
            'literature': self.download_literature_info,
            'normal': self.download_normal_info
        }

    def get_diseases_id(self):
        diseases_url = 'http://www.metagene.de/appl/diseases.prg?act=getData'
        str_json = self.get(diseases_url)
        correct = re.sub(r'([,|{])(\w+)(:)', r'\1"\2"\3', str_json)   # json数据格式化
        try:
            json_text = json.loads(correct)
        except JSONDecodeError:
            logger.warning('JSON 解析错误，3s后重新获取')
            time.sleep(3)
            return self.get_diseases_id()
        else:
            disease_ids = [i['id'] for i in json_text['rows']]
            return disease_ids

    # 搜索特定字段，除了 summary 以外
    def search(self, trs, text):
        for tr in trs:
            label = tr.find('label').get_text()
            value = tr.findAll('td')[-1].get_text().strip()
            if label == text and value not in ['', '---']:
                if text in ['OMIM', 'Orphanet']: # 这两个字段为数字，故统一处理
                    try:
                        value = re.findall(r'\d+', value)[0]
                    except IndexError:
                        value = ''
                if text == 'Gene locus':
                    str_raw = str(tr.findAll('td')[-1].contents[0])
                    value = str_raw if str_raw != '---' else ''
                return value

    def get_summary(self, trs): # 获取 summary 字段
        summary_contents = trs[-1].findAll('td')[-1].contents
        def make_str(element):
            if isinstance(element, Tag):
                element = element.get_text()
            element = str(element).strip()
            return element
        new_list = [make_str(i) for i in summary_contents]
        l = list(filter(lambda x: x != '', new_list)) # remove ''
        # 合并 summary ，比如有以下数据
        # rare (1:100000) 
        # autosomal recessive
        # mutation in the CYP11B1 gene
        result = '||'.join(l)
        return result
            
    def download_disease_info(self, queue, base_url):
        '''根据疾病 id 获取详情信息'''
        while True:
            disease_id = queue.get()
            if disease_id == 0:
                break
            url = base_url + str(disease_id)
            while True:
                html = self.get(url)
                soup = BeautifulSoup(html, 'lxml')
                trs = soup.findAll('tr')
                if trs != []: break
                # to-do: 更换代理
                logger.error('*'*10 + str(url) + ' 获取不到html元素，3秒后重试' + '*'*10)
                time.sleep(3)
                # return self.download_disease_info(disease_id)
            disease_name = self.search(trs, 'Disease')
            synonym = self.search(trs, 'Synonym')
            omim = self.search(trs, 'OMIM')
            orphanet = self.search(trs, 'Orphanet')
            protein = self.search(trs, 'Protein (UniProt)')
            expasy = self.search(trs, 'ExPASy')
            gene_locus = self.search(trs, 'Gene locus')
            icd = self.search(trs, 'ICD')
            summary = self.get_summary(trs)
            mysql.insert_disease(disease_name, synonym, omim, orphanet, protein, expasy, gene_locus, icd, summary, disease_id)
            time.sleep(1)   # 降低访问频率

    def download_symptom_info(self, queue, base_url):
        while True:
            lookup_id = queue.get()
            if lookup_id == 0: break
            url = base_url + str(lookup_id)
            fk_disease_id = mysql.select_disease_id(lookup_id)  # 查询疾病id
            if not fk_disease_id: continue   # 找不到对应id，则跳过
            html = self.get(url)
            json_symptoms = json.loads(html)
            for s in json_symptoms['rows']:
                symptom = s['data'][0]
                symptom_id =  mysql.select_symptom_id(symptom)  # 判断在症状表中是否存在
                if symptom_id:
                    if not mysql.select_ds(fk_disease_id, symptom_id):  # 在疾病-症状关联表中不存在
                        mysql.insert_ds(fk_disease_id, symptom_id)
                else:  # 症状不存在
                    category = s['data'][1]
                    mysql.insert_symptom(symptom, category, fk_disease_id)  # 插入症状表
                    symptom_id =  mysql.select_symptom_id(symptom)  # 查询症状id
                    mysql.insert_ds(fk_disease_id, symptom_id)  # 插入关联表
            time.sleep(1)

    def download_lab_info(self, queue, base_url):
        while True:
            disease_id = queue.get()
            if disease_id == 0: break
            url = base_url + str(disease_id)
            fk_disease_id = mysql.select_disease_id(disease_id)
            if not fk_disease_id: continue   # 找不到对应id，则跳过
            html = self.get(url)
            correct = re.sub(r'([,|{])(\w+)(:)', r'\1"\2"\3', html)
            json_info = json.loads(correct)
            for s in json_info['rows']:
                metabolite = s['data'][0]
                unit = s['data'][1]
                specimen = s['data'][2]
                agegroup = s['data'][3]
                min_value = s['data'][4]
                max_value = s['data'][5]
                mysql.insert_lab(metabolite, specimen, agegroup, min_value, max_value, unit, fk_disease_id)
            time.sleep(1)        

    def download_literature_info(self, queue, base_url):
        while True:
            lookup_id = queue.get()
            if lookup_id == 0: break
            url = base_url + str(lookup_id)
            fk_disease_id = mysql.select_disease_id(lookup_id)
            if not fk_disease_id: continue   # 找不到对应id，则跳过
            html = self.get(url)
            json_info = json.loads(html)
            for s in json_info['rows']:
                try:
                    title = re.findall(r'>(.*)<', s['data'][0])[0]
                except IndexError:
                    try:
                        title = re.findall(r'>(.*)', s['data'][0])[0]
                    except Exception as e:
                        print('[lookup_id %s]获取 title 出错，原因：%s' % (lookup_id, e))
                else:  # 获取不到<a>标签的内容，则跳过，因为link也获取不到了
                    try:
                        link = re.findall(r"(https?://.*)'", s['data'][0])[0]
                    except:  # 没有链接
                        print('获取link出错，url：', url)
                        print(title)
                    else:
                        literature_id = mysql.select_literature_id(title)
                        if literature_id:   # 文献已存在
                            if not mysql.select_dl(fk_disease_id, literature_id):  # 在关联表中不存在
                                mysql.insert_dl(fk_disease_id, literature_id)  # 添加疾病-文献关联关系
                        else:
                            author = s['data'][1]
                            journal = s['data'][2]
                            mysql.insert_literature(title, link, author, journal, fk_disease_id)  # 插入文献
                            literature_id = mysql.select_literature_id(title)  # 查询文献id
                            mysql.insert_dl(fk_disease_id, literature_id)  # 添加疾病-文献关联关系
            time.sleep(2)

    def download_normal_info(self, queue, base_url):
        while True:
            disease_id = queue.get()
            if disease_id == 0: break
            url = base_url + str(disease_id)
            fk_disease_id = mysql.select_disease_id(disease_id)
            if not fk_disease_id: continue   # 找不到对应id，则跳过
            html = self.get(url)
            json_info = json.loads(html)
            for s in json_info['rows']:
                metabolite = s['data'][0].strip()
                min_value = s['data'][1].strip()
                max_value = s['data'][2].strip()
                unit = s['data'][3].strip()
                specimen = s['data'][4].strip()
                agegroup = s['data'][5].strip()
                method = s['data'][6].strip()
                mysql.insert_normal(metabolite, min_value, max_value, unit, specimen, agegroup, method, fk_disease_id)
            time.sleep(1)

    def schedule(self, disease_id_list, base_url, cate):
        '''
        任务调度器

        :param list disease_id_list: 待处理的疾病关联编号
        :param str base_url: 用于与疾病编号连接，构成目标url
        :param str cate: 处理的数据类别：disease, symptom, lab, normal, literature 
        '''
        queue = Queue()  # 线程间通信
        download_tasks = []
        start = time.time()
        total = 0
        for i in disease_id_list:
            queue.put(i)
            total += 1
        logger.info('*'*10 + '[%s] the number of urls to be handled: [%s]' % (cate, total) + '*'*10)
        time.sleep(1)
        for _ in range(15):  # 开 15 个下载线程
            download_tasks.append(Thread(target=self.download_func[cate], args=(queue, base_url)))
            queue.put(0)
        logger.info('-'*10 + 'start downloading %s' % cate + '-'*10)
        for t in download_tasks:
            t.start()
        for t in download_tasks:
            t.join()
        logger.info('-'*10 + '[%s] the program takes %.2f s to handle %s urls' % (cate, time.time() - start, total) + '-'*10)
        



    



    