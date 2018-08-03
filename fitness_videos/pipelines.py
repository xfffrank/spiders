'''
数据库操作
'''
import pymongo
from settings import *
import logging

client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client[MONGO_DB]
coll = db[MONGO_COLL]
logger = logging.getLogger('fitness')

class Pipelines(object):

    @classmethod
    def insert(cls, item):
        '''
        插入已爬取的url

        :param dict item: 字典数据，例如{'url': 'http://xxxx'}

        '''
        try:
            coll.insert(item)
        except Exception as e:
            logger.warning(e)
        else:
            logger.info('%s 存储完毕', item['url'])

    @classmethod
    def find(cls, url):
        return True if coll.find_one({'url': url}) else False