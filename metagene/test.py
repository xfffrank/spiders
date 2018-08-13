# 测试静态方法的使用
# class Test(object):

#     a = 2

#     @staticmethod
#     def test():
#         print(Test.a)

# t = Test.test
# t()


# 测试 mysql SELECT EXISTS
import pymysql
from settings import *
connection = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWD,
    db=MYSQL_DB
)

with connection.cursor() as cursor:
    sql = """
    SELECT EXISTS(SELECT 1 FROM diseases WHERE disease_id = %s)
    """
    # sql = """
    # SELECT EXISTS(SELECT 1 FROM disease_literature WHERE disease_id = %s AND literature_id = %s)
    # """
    cursor.execute(sql, (14))
    result = cursor.fetchone()
# a = [value for value in result.values()]
print(result)
print(result[0])
