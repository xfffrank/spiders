'''数据库相关操作



数据库描述：

mysql> describe diseases;
+--------------+------------------+------+-----+---------+----------------+
| Field        | Type             | Null | Key | Default | Extra          |
+--------------+------------------+------+-----+---------+----------------+
| disease_id   | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| disease_name | varchar(150)     | NO   | UNI | NULL    |                |
| synonym      | varchar(150)     | YES  |     | NULL    |                |
| omim         | varchar(10)      | YES  |     | NULL    |                |
| orphanet     | varchar(10)      | YES  |     | NULL    |                |
| protein      | varchar(255)     | YES  |     | NULL    |                |
| expasy       | varchar(50)      | YES  |     | NULL    |                |
| gene_locus   | varchar(255)     | YES  |     | NULL    |                |
| icd          | varchar(50)      | YES  |     | NULL    |                |
| summary      | text             | NO   |     | NULL    |                |
| lookup_id    | int(10) unsigned | NO   |     | NULL    |                |
+--------------+------------------+------+-----+---------+----------------+

mysql> describe symptoms;
+--------------+------------------+------+-----+---------+----------------+
| Field        | Type             | Null | Key | Default | Extra          |
+--------------+------------------+------+-----+---------+----------------+
| symptom_id   | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| symptom_name | varchar(100)     | NO   | UNI | NULL    |                |
| category     | varchar(100)     | NO   |     | NULL    |                |
| disease_id   | int(10) unsigned | NO   | MUL | NULL    |                |
+--------------+------------------+------+-----+---------+----------------+

mysql> describe literature;
+---------------+------------------+------+-----+---------+----------------+
| Field         | Type             | Null | Key | Default | Extra          |
+---------------+------------------+------+-----+---------+----------------+
| literature_id | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| title         | varchar(255)     | NO   | UNI | NULL    |                |
| link          | varchar(120)     | NO   |     | NULL    |                |
| author        | varchar(30)      | NO   |     | NULL    |                |
| journal       | varchar(255)     | NO   |     | NULL    |                |
| disease_id    | int(10) unsigned | NO   | MUL | NULL    |                |
+---------------+------------------+------+-----+---------+----------------+

mysql> describe lab;
+------------+------------------+------+-----+---------+----------------+
| Field      | Type             | Null | Key | Default | Extra          |
+------------+------------------+------+-----+---------+----------------+
| lab_id     | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| metabolite | varchar(100)     | NO   |     | NULL    |                |
| specimen   | varchar(30)      | YES  |     | NULL    |                |
| agegroup   | varchar(30)      | YES  |     | NULL    |                |
| min_value  | varchar(10)      | YES  |     | NULL    |                |
| max_value  | varchar(10)      | YES  |     | NULL    |                |
| unit       | varchar(25)      | YES  |     | NULL    |                |
| disease_id | int(10) unsigned | NO   | MUL | NULL    |                |
+------------+------------------+------+-----+---------+----------------+

mysql> describe normal_specimens;
+------------+------------------+------+-----+---------+----------------+
| Field      | Type             | Null | Key | Default | Extra          |
+------------+------------------+------+-----+---------+----------------+
| ns_id      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| metabolite | varchar(100)     | NO   |     | NULL    |                |
| min_value  | varchar(10)      | YES  |     | NULL    |                |
| max_value  | varchar(10)      | YES  |     | NULL    |                |
| unit       | varchar(25)      | NO   |     | NULL    |                |
| specimen   | varchar(30)      | NO   |     | NULL    |                |
| agegroup   | varchar(30)      | NO   |     | NULL    |                |
| method     | varchar(10)      | YES  |     | NULL    |                |
| disease_id | int(10) unsigned | NO   | MUL | NULL    |                |
+------------+------------------+------+-----+---------+----------------+

mysql> describe disease_symptom;
+------------+------------------+------+-----+---------+----------------+
| Field      | Type             | Null | Key | Default | Extra          |
+------------+------------------+------+-----+---------+----------------+
| ds_id      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| disease_id | int(10) unsigned | NO   | MUL | NULL    |                |
| symptom_id | int(10) unsigned | NO   | MUL | NULL    |                |
+------------+------------------+------+-----+---------+----------------+

mysql> describe disease_literature;
+---------------+------------------+------+-----+---------+----------------+
| Field         | Type             | Null | Key | Default | Extra          |
+---------------+------------------+------+-----+---------+----------------+
| dl_id         | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
| disease_id    | int(10) unsigned | NO   | MUL | NULL    |                |
| literature_id | int(10) unsigned | NO   | MUL | NULL    |                |
+---------------+------------------+------+-----+---------+----------------+

'''

import pymysql
import pymongo
from settings import *
import logging
from threading import Lock

connection = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWD,
    db=MYSQL_DB
)

# client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
# db = client[MONGO_DB]
# coll_dict = {
#     'disease': db[MONGO_COLL_DISEASES],  # 疾病
#     'symptom': db[MONGO_COLL_SYMPTOMS],  # 症状
#     'lab': db[MONGO_COLL_LAB],  # 实验数据
#     'literature': db[MONGO_COLL_LITERATURE],  # 相关文献
#     'normal': db[MONGO_COLL_NP]  # 正常样本
# }
logger = logging.getLogger(LOGGER)
lock = Lock()   # 互斥锁，用于线程同步，使所有线程可以共享一个 mysql 连接

class MySQLPipelines(object):

    @classmethod
    def insert_disease(cls, disease_name, synonym, omim, orphanet, protein, expasy, gene_locus, icd, summary, disease_id):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO diseases (disease_name, 
                synonym, omim, orphanet, protein, expasy, gene_locus, icd, summary, lookup_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (disease_name, synonym, omim, orphanet, protein, expasy, gene_locus, icd, summary, disease_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql | disease] %s' % e)
            logger.warning('[disease | failure] %s' % disease_name)
        else:
            logger.info('[disease | success] %s' % disease_name)
            # MongoPipelines.insert(disease_id, category='disease')
        finally:
            lock.release()   # 操作成功或失败都需要释放线程锁

    @classmethod
    def insert_symptom(cls, symptom_name, category, disease_id):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO symptoms (symptom_name, category, disease_id) 
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (symptom_name, category, disease_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql | symptoms] %s' % e)
            logger.warning('[symptoms | failure] %s' % symptom_name)
        else:
            logger.info('[symptoms | success] %s' % symptom_name)
            # MongoPipelines.insert(disease_id, category='symptom')
        finally:
            lock.release()

    @classmethod
    def insert_literature(cls, title, link, author, journal, disease_id):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO literature (title, link, author, journal, disease_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (title, link, author, journal, disease_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql | literature] %s' % e)
            logger.warning('[literature | failure] %s' % title)
        else:
            logger.info('[literature | success] %s' % title)
            # MongoPipelines.insert(disease_id, category='literature')
        finally:
            lock.release()

    @classmethod
    def insert_lab(cls, metabolite, specimen, agegroup, min_value, max_value, unit, disease_id):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO lab (metabolite, specimen, agegroup, min_value, max_value, unit, disease_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (metabolite, specimen, agegroup, min_value, max_value, unit, disease_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql | lab] %s' % e)
            logger.warning('[lab | failure] %s' % metabolite)
        else:
            logger.info('[lab | success] %s' % metabolite)
            # MongoPipelines.insert(disease_id, category='lab')
        finally:
            lock.release()

    @classmethod
    def insert_normal(cls, metabolite, min_value, max_value, unit, specimen, agegroup, method, disease_id):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO normal_specimens (metabolite, min_value, max_value, unit, specimen, agegroup, method, disease_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (metabolite, min_value, max_value, unit, specimen, agegroup, method, disease_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql | normal] %s' % e)
            logger.warning('[normal | failure] %s' % metabolite)
        else:
            logger.info('[normal | success] %s' % metabolite)
            # MongoPipelines.insert(disease_id, category='normal')
        finally:
            lock.release()

    @classmethod
    def select_disease_id(cls, lookup_id):
        '''
        在 diseases 表中查询对应 lookup_id 的主键
        '''
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                SELECT disease_id FROM diseases WHERE lookup_id = %s
                """
                cursor.execute(sql, (lookup_id,))
                result = cursor.fetchone()[0]
        except Exception as e:
            logger.error('[mysql | select] %s' % e)
            return 0
            # logger.warning('[symptoms | failure] %s' % symptom_name)
        else:
            return result
        finally:
            lock.release()

    @classmethod
    def select_ds(cls, disease_id, symptom_id):
        '''
        根据疾病id和症状id从疾病-症状关联表中查询数据
        '''
        lock.acquire()
        with connection.cursor() as cursor:
            sql = """
            SELECT EXISTS(SELECT 1 FROM disease_symptom WHERE disease_id = %s AND symptom_id = %s)
            """
            cursor.execute(sql, (disease_id, symptom_id))
            result_tuple = cursor.fetchone()
            lock.release()
        return result_tuple[0]
        
    @classmethod
    def select_dl(cls, disease_id, literature_id):
        '''
        根据疾病id和文献id从疾病-文献关联表中查询数据
        '''
        lock.acquire()
        with connection.cursor() as cursor:
            sql = """
            SELECT EXISTS(SELECT 1 FROM disease_literature WHERE disease_id = %s AND literature_id = %s)
            """
            cursor.execute(sql, (disease_id, literature_id))
            result_tuple = cursor.fetchone()
            lock.release()
        return result_tuple[0]

    @classmethod
    def insert_ds(cls, disease_id, symptom_id):
        '''
        插入疾病-症状关联数据
        '''
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO disease_symptom(disease_id, symptom_id) VALUES(%s, %s)
                """
                cursor.execute(sql, (disease_id, symptom_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql|ds] %s' % e)
        else:
            logger.info('[ds | success] %s, %s' % (disease_id, symptom_id))
        finally:
            lock.release()

    @classmethod
    def insert_dl(cls, disease_id, literature_id):
        '''
        插入疾病-文献关联数据
        '''
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO disease_literature(disease_id, literature_id) VALUES(%s, %s)
                """
                cursor.execute(sql, (disease_id, literature_id))
            connection.commit()
        except Exception as e:
            logger.error('[mysql|dl] %s' % e)
        else:
            logger.info('[dl | success] %s, %s' % (disease_id, literature_id))
        finally:
            lock.release()     

    @classmethod
    def select_symptom_id(cls, symptom_name):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                SELECT symptom_id FROM symptoms WHERE symptom_name = %s
                """
                cursor.execute(sql, (symptom_name,))
                result = cursor.fetchone()[0]
        except Exception as e:
            # logger.debug('[mysql | select] %s' % e)
            return 0
        else:
            return result
            # logger.warning('[symptoms | failure] %s' % symptom_name)
        finally:
            lock.release()

    @classmethod
    def select_literature_id(cls, title):
        try:
            lock.acquire()
            with connection.cursor() as cursor:
                sql = """
                SELECT literature_id FROM literature WHERE title = %s
                """
                cursor.execute(sql, (title,))
                result = cursor.fetchone()[0]
        except Exception as e:
            # logger.error('[mysql | select] %s' % e)
            return 0
        else:
            return result
            # logger.warning('[symptoms | failure] %s' % symptom_name)
        finally:
            lock.release()
