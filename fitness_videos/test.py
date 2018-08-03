'''
测试文件
'''
import requests, time
from bs4 import BeautifulSoup
from selenium import webdriver

def request(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        'Referer': 'http://www.hiyd.com/dongzuo/'
    }
    response = requests.get(url, headers=headers)
    return response

# options.add_argument('user-agent="Mozilla/5.0 dddd",--headless')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"')

driver = webdriver.Chrome('D:\programs\chromedriver.exe', chrome_options=chrome_options)
driver.get('http://www.hiyd.com/dongzuo/1/')
time.sleep(2)
driver.find_element_by_class_name('coach-woman').click()
time.sleep(2)
soup = BeautifulSoup(driver.page_source, 'lxml')
video_page = request(soup.find('video')['src'])
with open('test_8_2.mp4', 'ab') as f:
    f.write(video_page.content)
driver.close()
