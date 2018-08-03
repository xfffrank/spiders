from downloader import *
from bs4 import BeautifulSoup
import logging
from threading import Thread
import time
from queue import Queue
from pipelines import Pipelines as db

base_url = 'http://www.hiyd.com'

class Spider(Downloader):

    def __init__(self):
        logger.info('[spider opened]')
        super().__init__()

    def start_requests(self):
        q = Queue()  # 详情链接队列
        flag = 0   # 标记 waiting_list.txt 文件是否存在
        try:
            with open('txt/waiting_list.txt') as f:
                waiting_list = f.readlines()
            flag = 1
        except:
            logger.info('获取单页面链接.....')
            page_num = 80
            workers = []
            for num in range(1, page_num + 1):
                url = 'http://www.hiyd.com/dongzuo/?page=%s' % str(num)
                workers.append(Thread(target=self.parse, args=(url,)))
            for w in workers:
                w.start()
            for w in workers:
                w.join()
            logger.info('单页面链接获取完毕.....')
        if not flag:    # try 语句执行未通过，执行了except代码
            with open('txt/waiting_list.txt') as f:
                waiting_list = f.readlines()
        count = 0
        for i in waiting_list:
            url = i.strip()
            if url and not db.find(url):   # 非空行且还未爬取
                q.put(url)
                count += 1
        logger.info("未下载的视频数量：%s" % count)
        video_workers = []   # 下载视频的线程池
        for _ in range(20):  # 开启 20 个线程用于下载视频
            video_workers.append(Thread(target=self.download_one_video, args=(q,)))
            q.put(0)   #　线程终止条件标记
        start = time.time()
        logger.info('开始下载视频')
        for w in video_workers:
            w.start()
        for w in video_workers:
            w.join()
        logger.info('[下载时间]: %.2f s' % (time.time() - start))

    def parse(self, url):
        response = self.request(url)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('li', class_='hvr-glow')
        for i in items:
            href = i.find('a')['href']
            url = base_url + href
            with open('txt/waiting_list.txt', 'a') as f:
                f.write(url + '\n')

    def download_one_video(self, q):
        while(1):
            url = q.get()
            if url == 0:
                break
            # print(url)
            driver = self.get(url)   # 使用 selenium 才能定位到视频元素
            try:
                driver.find_element_by_class_name('coach-woman').click()
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, 'jp_poster_0'))  
                )
            except:
                print(url, '没有女教练视频')
                soup = BeautifulSoup(driver.page_source, 'lxml')
            else:
                print(url, '找到女教练视频')
                soup = BeautifulSoup(driver.page_source, 'lxml')
            finally:
                # driver.close()
                driver.quit()
            try:
                video_page = self.request(soup.find('video')['src'])
            except Exception as e:
                logger.error(e)
                logger.error(url)
            else:
                video_id = re.findall(r'\d+', url)[0]   # 视频编号
                with open('videos/{}.mp4'.format(video_id), 'ab') as f:
                    f.write(video_page.content)
                logger.info('{}:视频下载完毕'.format(video_id))
                item = {'url': url}
                db.insert(item)
                # with open('txt/crawled_urls.txt', 'a') as f:
                #     f.write(url + '\n')   # 记录已下载的视频链接
            time.sleep(1.5)   # 睡眠 1.5 秒，降低访问频率

if __name__ == '__main__':
    s = Spider()
    s.start_requests()
    # time.sleep(8)
    # print(total)


#  to-do
# 使用 mongo 去重
# 将获取视频url和下载视频的模块分开