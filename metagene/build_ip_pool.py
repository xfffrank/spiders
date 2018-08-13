'''
建立代理池
'''
import requests
from bs4 import BeautifulSoup
from threading import Thread
import time
from multiprocessing import Pool, Process, Queue

class GetIp(object):

    def __init__(self, verify_site):
        self.proxy_list = []
        self.site = verify_site
    
    def get_proxy_ip(self):
        start = time.time()
        print('start crawling ip...')
        try:
            html = requests.get('http://www.xicidaili.com/', headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
            })
        except Exception as e:
            print(e)
        soup = BeautifulSoup(html.text, 'lxml')
        trs = soup.find('table', id='ip_list').find_all('tr', class_=['', 'odd'])[2:]
        for tr in trs:
            scheme = tr.findAll('td', class_="")[-3].get_text().lower()
            if scheme in ['http', 'https']:
                ip = tr.findAll('td', class_="")[0].get_text()
                port = tr.findAll('td', class_="")[1].get_text()
                ip_info = scheme + '://' + ip + ':' + port
                self.proxy_list.append(ip_info)
        # print(self.proxy_list)
        print('total time: %.2f' % (time.time() - start))
    
    def verify_proxies(self):
        start = time.time()
        old_queue = Queue()
        new_queue = Queue()
        print('verify proxies...')
        workers = []
        for _ in range(15):
            # 多进程
            # workers.append(Process(target=self.verify_one_ip, args=(old_queue, new_queue)))
            # 多线程
            workers.append(Thread(target=self.verify_one_ip, args=(old_queue, new_queue)))
        for w in workers:
            w.start()
        for ip in self.proxy_list:
            old_queue.put(ip)
        for w in workers:
            old_queue.put(0)
        for w in workers:
            w.join()
        self.proxy_list = []
        while(1):
            try:
                self.proxy_list.append(new_queue.get(timeout=1))
            except:
                break
        print('[verification] total time: %.2f s' % (time.time() - start))
        print('proxies verified !')

    def verify_one_ip(self, old_queue, new_queue):
        while 1:
            proxy = old_queue.get()
            if proxy == 0:
                break
            protocol = 'https' if 'https' in proxy else 'http'
            proxies = {
                protocol: proxy
            }
            try:
                if requests.get(self.site, timeout=3, proxies=proxies).status_code == 200:
                    print('[success] %s' % proxy)
                    new_queue.put(proxy)
            except:
                print('[fail] %s' % proxy)

# if __name__ == '__main__':
#     print('Test Site: {}'.format('http://www.hiyd.com/dongzuo/'))
#     g = GetIp()
#     g.get_proxy_ip()
#     g.verify_proxies()
#     with open('proxies.txt', 'w') as f:
#         for proxy in g.proxy_list:
#             f.write(proxy + '\n')

# g = GetIp(4)
# g.handle_tasks_mt()

