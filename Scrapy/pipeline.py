import pymysql

class MysqlPipeline(object):
    def __init__(self):
        self.db = None

    def open_spider(self, spider):
        self.db = pymysql.connect(host='localhost', user='root', password='password', db='database_name', charset='utf8')

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        # 将item转换为DataFrame
        import pandas
        df = pandas.DataFrame([item], columns=item.keys())
        # 将DataFrame写入MySQL
        df.to_sql(name='table_name', con=self.db, if_exists='append', index=False)
        return item
