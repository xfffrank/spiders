'''
下载器
'''
import requests
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

logger = logging.getLogger('fitness')
logger.setLevel(logging.DEBUG)  # 设置 scrapy 控制台的日志输出级别
ch = logging.StreamHandler()
fh = logging.FileHandler('log/download.log', encoding='utf-8', mode='a')  # w 覆盖原文件，a 追加
fh.setLevel(logging.INFO)   # 设置重定向文件的日志输出级别
ch.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)

class Downloader(object):

    def __init__(self):
        self.proxy_list_s = []   # 供 selenium 使用的代理
        with open('proxies.txt') as f:
            self.proxy_list_r = f.readlines()   # 供 requests 使用的代理
        for ip in self.proxy_list_r:
            trimmed = re.findall(r'//(.*)', ip)[0]
            self.proxy_list_s.append(trimmed)
        self.selenium_proxy = random.choice(self.proxy_list_s).strip()
        self.requests_proxy = random.choice(self.proxy_list_r).strip()
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

    def request(self, url):
        headers = {
            'User-Agent': random.choice(self.user_agent_list),
            'Referer': 'http://www.hiyd.com/dongzuo/'  # 破解视频反盗链
        }
        protocol = 'https' if 'https' in self.requests_proxy else 'http'
        proxies = {
            protocol: self.requests_proxy
        }
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        except:
            logger.debug('[requests]正在更换代理ip...')
            self.requests_proxy = random.choice(self.proxy_list_r).strip()
            return self.request(url)
        else:
            return response

    def get(self, url):
        '''
        selenium 使用代理和随机user-agent发送请求，获取网页源码
        selenium 默认支持 http 和 https 的代理地址

        :param str url: 目标资源位置
        '''
        options = webdriver.ChromeOptions()
        user_agent = 'user-agent="%s"' % random.choice(self.user_agent_list)
        proxy = '--proxy-server=%s' % self.selenium_proxy
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument(user_agent)
        options.add_argument(proxy)
        try:
            driver = webdriver.Chrome('D:\programs\chromedriver.exe', chrome_options=options)
            driver.get(url)
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, 'jp_poster_0'))  
            )
            # WebDriverWait(driver, 2).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, 'share-handler'))
            # )
        except:
            logger.debug('[selenium]正在更换代理ip...')
            self.selenium_proxy = random.choice(self.proxy_list_s).strip()
            driver.quit()  # kill 当前 driver 实例，节省内存
            return self.get(url)
        else:
            return driver
            