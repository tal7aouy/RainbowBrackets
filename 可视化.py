# -*- coding: utf-8 -*-

# 数据爬取文件

import scrapy
import pymysql
import pymssql
from ..items import DianyingxinxiItem
import time
from datetime import datetime,timedelta
import datetime as formattime
import re
import random
import platform
import json
import os
import urllib
from urllib.parse import urlparse
import requests
import emoji
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver import ChromeOptions, ActionChains
from scrapy.http import TextResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# 电影信息
class DianyingxinxiSpider(scrapy.Spider):
    """豆瓣电影爬虫类"""
    
    name = 'dianyingxinxiSpider'
    allowed_domains = ['douban.com']
    
    # 基础URL
    base_url = 'https://m.douban.com/rexxar/api/v2/movie/recommend'
    
    # 请求参数
    params = {
        'refresh': '0',
        'count': '20',
        'selected_categories': '{"类型":"喜剧"}',
        'uncollect': 'false',
        'tags': '喜剧',
        'ck': 'IsFz'
    }
    
    def __init__(self, *args, **kwargs):
        super(DianyingxinxiSpider, self).__init__(*args, **kwargs)
        self.driver = None
        self.protocol = urlparse(self.base_url).scheme
    
    def start_requests(self):
        """生成初始请求"""
        for start in range(0, 100, 20):  # 获取100条数据
            self.params['start'] = str(start)
            url = f"{self.base_url}?{'&'.join(f'{k}={v}' for k,v in self.params.items())}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=self._get_headers(),
                dont_filter=True
            )
    
    def _get_headers(self):
        """获取请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://movie.douban.com/'
        }
    
    def parse(self, response):
        """解析响应数据"""
        try:
            data = json.loads(response.text)
            for item in data.get('items', []):
                movie = DianyingxinxiItem()
                movie['title'] = item.get('title')
                movie['rating'] = item.get('rating', {}).get('value')
                movie['url'] = item.get('url')
                yield movie
                
        except Exception as e:
            self.logger.error(f'解析错误: {str(e)}')

    def close(self, reason):
        """关闭爬虫时清理资源"""
        if self.driver:
            self.driver.quit()
        super(DianyingxinxiSpider, self).close(reason)

    # 数据清洗
    def pandas_filter(self):
        engine = create_engine('mysql+pymysql://root:123456@localhost/spiderc2xklu0u?charset=UTF8MB4')
        df = pd.read_sql('select * from dianyingxinxi limit 50', con = engine)

        # 重复数据过滤
        df.duplicated()
        df.drop_duplicates()

        #空数据过滤
        df.isnull()
        df.dropna()

        # 填充空数据
        df.fillna(value = '暂无')

        # 异常值过滤

        # 滤出 大于800 和 小于 100 的
        a = np.random.randint(0, 1000, size = 200)
        cond = (a<=800) & (a>=100)
        a[cond]

        # 过滤正态分布的异常值
        b = np.random.randn(100000)
        # 3σ过滤异常值，σ即是标准差
        cond = np.abs(b) > 3 * 3
        b[cond]

        # 正态分布数据
        df2 = pd.DataFrame(data = np.random.randn(10000,3))
        # 3σ过滤异常值，σ即是标准差
        cond = (df2 > 3*df2.std()).any(axis = 1)
        # 不满?条件的?索引
        index = df2[cond].index
        # 根据?索引，进?数据删除
        df2.drop(labels=index,axis = 0)

    # 去除多余html标签
    def remove_html(self, html):
        if html == None:
            return ''
        pattern = re.compile(r'<[^>]+>', re.S)
        return pattern.sub('', html).strip()

    # 数据库连接
    def db_connect(self):
        type = self.settings.get('TYPE', 'mysql')
        host = self.settings.get('HOST', 'localhost')
        port = int(self.settings.get('PORT', 3306))
        user = self.settings.get('USER', 'root')
        password = self.settings.get('PASSWORD', '123456')

        try:
            database = self.databaseName
        except:
            database = self.settings.get('DATABASE', '')

        if type == 'mysql':
            connect = pymysql.connect(host=host, port=port, db=database, user=user, passwd=password, charset='utf8')
        else:
            connect = pymssql.connect(host=host, user=user, password=password, database=database)
        return connect

    # 断表是否存在
    def table_exists(self, cursor, table_name):
        cursor.execute("show tables;")
        tables = [cursor.fetchall()]
        table_list = re.findall(r"'(.*?)'",str(tables))
        table_list = [re.sub("'",'',each) for each in table_list]

        if table_name in table_list:
            return 1
        else:
            return 0

    # 数据缓存源
    def temp_data(self):

        connect = self.db_connect()
        cursor = connect.cursor()
        sql = '''
            insert into `dianyingxinxi`(
                id
                ,title
                ,year
                ,picture
                ,ypxx
                ,pingfen
                ,pjs
                ,wxs
                ,tags
                ,plnr
                ,uname
                ,xqdz
            )
            select
                id
                ,title
                ,year
                ,picture
                ,ypxx
                ,pingfen
                ,pjs
                ,wxs
                ,tags
                ,plnr
                ,uname
                ,xqdz
            from `c2xklu0u_dianyingxinxi`
            where(not exists (select
                id
                ,title
                ,year
                ,picture
                ,ypxx
                ,pingfen
                ,pjs
                ,wxs
                ,tags
                ,plnr
                ,uname
                ,xqdz
            from `dianyingxinxi` where
                `dianyingxinxi`.id=`c2xklu0u_dianyingxinxi`.id
            ))
            order by rand()
            limit 50;
        '''

        cursor.execute(sql)
        connect.commit()
        connect.close()










# coding:utf-8
__author__ = "ila"

import logging
import os
import json
import configparser
import time
from datetime import datetime
from flask import request, jsonify, session
from sqlalchemy.sql import func,and_,or_,case
from sqlalchemy import cast, Integer,Float
from api.models.brush_model import * # type: ignore
try:
    from api.models.dianyingxinxi_model import dianyingxinxi
except ImportError:
    dianyingxinxi = None
from utils.codes import *
from utils.jwt_auth import Auth  
from configs import configs
from utils.helper import *
from api.models.config_model import config
try:
    from utils.baidubce_api import BaiDuBce
except ImportError:
    BaiDuBce = None
except ImportError:
    # Define fallback classes/variables if imports fail
    dianyingxinxi = None
    Auth = None
    configs = {}
    BaiDuBce = None
    config = None
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr 
from email.header import Header

# Initialize main_bp if not defined
try:
    from . import main_bp
except ImportError:
    from flask import Blueprint
    main_bp = Blueprint('main', __name__)



from flask import current_app as app
try:
    from utils.spark_func import spark_read_mysql
except ImportError:
    spark_read_mysql = None
from utils.hdfs_func import upload_to_hdfs
try:
    from utils.mapreduce1 import MRMySQLAvg
except ImportError:
    MRMySQLAvg = None
from decimal import Decimal
from decimal import Decimal

def decimalEncoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


# 1. 基础导入
import os
from flask import Flask, request, jsonify, session, Blueprint
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 2. 常量定义
normal_code = 0 
crud_error_code = 500
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def create_spark_session():
    return SparkSession.builder \
        .appName("Movie Analysis") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

from pyspark.sql.functions import avg, count

def process_movie_data(df):
    return df.groupBy("category").agg(
        avg("rating").alias("avg_rating"),
        count("*").alias("count")
    )

import requests
import json    
class BaiduAPI:
        def __init__(self, api_key, secret_key):
            self.api_key = api_key
            self.secret_key = secret_key
            self.access_token = self._get_access_token()
        
        import os
        import sys
        from pathlib import Path
        from flask import Flask, request, jsonify, session, Blueprint
        from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from decimal import Decimal
        import json
        import requests

        # 添加项目根目录到系统路径
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))

        try:
            from utils.spark_func import create_spark_session, process_movie_data
            from utils.baidu_api import BaiduAPI
        except ImportError as e:
            print(f"Import Error: {e}")
            create_spark_session = None
            process_movie_data = None
            BaiduAPI = None

        # 配置信息
        CONFIG = {
            'database': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'your-password',
                'database': 'movie_db'
            },
            'baidu_api': {
                'api_key': 'your-api-key',
                'secret_key': 'your-secret-key'
            },
            'token_secret': 'your-token-secret'
        }

        # 工具函数
        def decimalEncoder(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return obj

        # 数据库连接
        def get_db_connection():
            try:
                engine = create_engine(


                    f"mysql+pymysql://{DATABASE['user']}:{DATABASE['password']}@"
                    f"{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
                )
                Session = sessionmaker(bind=engine)
                return Session()
            except Exception as e:
                print(f"Database connection error: {e}")
                return None

        # 初始化百度API
        baidu_api = BaiduAPI(
            CONFIG['baidu_api']['api_key'],
            CONFIG['baidu_api']['secret_key']
        ) if BaiduAPI else None

        class BaiduAPI:
            def __init__(self, api_key, secret_key):
                self.api_key = api_key
                self.secret_key = secret_key
                self.access_token = self._get_access_token()

            def _get_access_token(self):
                url = "https://aip.baidubce.com/oauth/2.0/token"
                params = {
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.secret_key
                }
                response = requests.get(url, params=params)
                return response.json().get("access_token")
Base = declarative_base()

# 3. 数据库配置
DATABASE = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root', 
    'password': 'password',
    'database': 'movie_db'
}

# 4. 创建数据库模型
class Dianyingxinxi(Base):
    __tablename__ = 'dianyingxinxi'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(Text)
    addtime = Column(DateTime)
    # ...其他字段

    @staticmethod
    def page(cls, table, req_dict):
        '''分页查询方法'''
        try:
            page = int(req_dict.get('page', 1))
            limit = int(req_dict.get('limit', 10))
            # 分页逻辑
            total = cls.query.count()
            items = cls.query.offset((page-1)*limit).limit(limit).all()
            return items, page, (total-1)//limit + 1, total, limit
        except Exception as e:
            return [], 1, 0, 0, 10

    @staticmethod 
    def createbyreq(cls, table, req_dict):
        '''创建记录方法'''
        try:
            model = cls()
            for key in req_dict:
                if hasattr(model, key):
                    setattr(model, key, req_dict[key])
            db.session.add(model)
            db.session.commit()
            return None
        except Exception as e:
            return str(e)

# 5. 创建蓝图实例
main_bp = Blueprint('main', __name__)

# 6. 数据库实例
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 7. 修复原有代码
@main_bp.route("/python9532dr50/dianyingxinxi/save", methods=['POST'])
def python9532dr50_dianyingxinxi_save():
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        
        if not req_dict:
            msg['code'] = crud_error_code
            msg['msg'] = "请求数据为空"
            return jsonify(msg)

        for key in req_dict:
            if req_dict[key] == '':
                req_dict[key] = None

        error = Dianyingxinxi.createbyreq(Dianyingxinxi, Dianyingxinxi, req_dict)
        if error is not None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        
        return jsonify(msg)

# 注册接口
@main_bp.route("/python9532dr50/dianyingxinxi/register", methods=['POST'])
def python9532dr50_dianyingxinxi_register():
    if request.method == 'POST':
        msg = {'code': normal_code, 'message': 'success', 'data': [{}]}
        req_dict = session.get("req_dict")


        error = dianyingxinxi.createbyreq(dianyingxinxi, dianyingxinxi, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = "注册用户已存在"
        return jsonify(msg)

# 登录接口
@main_bp.route("/python9532dr50/dianyingxinxi/login", methods=['GET','POST'])
def python9532dr50_dianyingxinxi_login():
    if request.method == 'GET' or request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        req_model = session.get("req_dict")
        try:
            del req_model['role']
        except:
            pass


        datas = dianyingxinxi.getbyparams(dianyingxinxi, dianyingxinxi, req_model)
        if not datas:
            msg['code'] = password_error_code
            msg['msg']='密码错误或用户不存在'
            return jsonify(msg)


        req_dict['id'] = datas[0].get('id')
        try:
            del req_dict['mima']
        except:
            pass


        return Auth.authenticate(Auth, dianyingxinxi, req_dict)


# 登出接口
@main_bp.route("/python9532dr50/dianyingxinxi/logout", methods=['POST'])
def python9532dr50_dianyingxinxi_logout():
    if request.method == 'POST':
        msg = {
            "msg": "退出成功",
            "code": 0
        }
        req_dict = session.get("req_dict")

        return jsonify(msg)

# 重置密码接口
@main_bp.route("/python9532dr50/dianyingxinxi/resetPass", methods=['POST'])
def python9532dr50_dianyingxinxi_resetpass():
    '''
    '''
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success"}

        req_dict = session.get("req_dict")

        if req_dict.get('mima') != None:
            req_dict['mima'] = '123456'

        error = dianyingxinxi.updatebyparams(dianyingxinxi, dianyingxinxi, req_dict)

        if error != None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        else:
            msg['msg'] = '密码已重置为：123456'
        return jsonify(msg)

# 获取会话信息接口
@main_bp.route("/python9532dr50/dianyingxinxi/session", methods=['GET'])
def python9532dr50_dianyingxinxi_session():
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "data": {}}
        req_dict={"id":session.get('params').get("id")}
        msg['data']  = dianyingxinxi.getbyparams(dianyingxinxi, dianyingxinxi, req_dict)[0]

        return jsonify(msg)

# 分类接口（后端）
@main_bp.route("/python9532dr50/dianyingxinxi/page", methods=['GET'])
def python9532dr50_dianyingxinxi_page():
    """
    分页获取电影信息
    """
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = request.args.to_dict()
        
        # 处理userid
        if 'userid' in req_dict.keys():
            del req_dict["userid"]

        if 'discuss' in 'dianyingxinxi':
            if 'userid' in req_dict.keys():
                del req_dict["userid"]

        # 获取分页数据
        msg['data']['list'], msg['data']['currPage'], \
        msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize'] = dianyingxinxi.page(dianyingxinxi, 
                                                    dianyingxinxi, 
                                                    req_dict)

        return jsonify(msg)

# 排序接口
@main_bp.route("/python9532dr50/dianyingxinxi/autoSort", methods=['GET'])
def python9532dr50_dianyingxinxi_autosort():
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success",  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = session.get("req_dict")
        req_dict['sort']='clicktime'
        req_dict['order']='desc'

        try:
            __browseClick__= dianyingxinxi.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__ =='是':
            req_dict['sort']='clicknum'
        elif __browseClick__ =='时长':
            req_dict['sort']='browseduration'
        else:
            req_dict['sort']='clicktime'
        req_dict = request.args.to_dict()
        req_dict = request.args.to_dict()
        req_dict = request.args.to_dict()
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], msg['data']['pageSize'] = dianyingxinxi.page(dianyingxinxi, dianyingxinxi, req_dict)

    return jsonify(msg)

# 分页接口（前端）
@main_bp.route("/python9532dr50/dianyingxinxi/list", methods=['GET'])
def python9532dr50_dianyingxinxi_list():
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success",  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = session.get("req_dict")
        if req_dict.__contains__('vipread'):
            del req_dict['vipread']
            
        userinfo = session.get("params")

        try:
            __foreEndList__=dianyingxinxi.__foreEndList__
        except:
            __foreEndList__=None

        if __foreEndList__ and __foreEndList__!="否":
            tablename=session.get("tablename")
            if tablename!="users" and session.get("params")!=None:
                req_dict['userid']=session.get("params").get("id")

        try:
            __foreEndListAuth__=dianyingxinxi.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否":
            tablename=session.get("tablename")
            if tablename!="users" and session.get("params")!=None:
                req_dict['userid']=session.get("params").get("id")

        tablename=session.get("tablename")
        if tablename=="users" :
            try:
                del req_dict["userid"]
            except:
                pass
        else:
            mapping_str_to_object = {}
            for model in Base._decl_class_registry.values():
                if hasattr(model, '__tablename__'):
                    mapping_str_to_object[model.__tablename__] = model

            try:
                __isAdmin__=mapping_str_to_object[tablename].__isAdmin__
            except:
                __isAdmin__=None

            if __isAdmin__!="是" and session.get("params")!=None:
                req_dict["userid"]=session.get("params").get("id")

        if 'luntan' in 'dianyingxinxi':
            if 'userid' in req_dict.keys():
                del req_dict["userid"]


        if 'discuss' in 'dianyingxinxi':
            if 'userid' in req_dict.keys():
                del req_dict["userid"]

msg = {"code": normal_code, "msg": "success", "data": {"list": [], "currPage": 1, "totalPage": 1, "total": 0, "pageSize": 10}}
msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], msg['data']['pageSize'] = dianyingxinxi.page(dianyingxinxi, dianyingxinxi, session.get("req_dict", {}))

def get_response():
    return jsonify(msg)

get_response()

# 保存接口（后端）
@main_bp.route("/python9532dr50/dianyingxinxi/save", methods=['POST'])
def python9532dr50_dianyingxinxi_save():
    """
    保存电影信息
    """
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        
        # 处理空值
        for key in req_dict:
            if req_dict[key] == '':
                req_dict[key] = None

        # 创建记录
        error = dianyingxinxi.createbyreq(dianyingxinxi, dianyingxinxi, req_dict)
        if error is not None:
            msg['code'] = crud_error_code
            msg['msg'] = error
            
        return jsonify(msg)

# 添加接口（前端）
@main_bp.route("/python9532dr50/dianyingxinxi/add", methods=['POST'])
def python9532dr50_dianyingxinxi_add():
    '''
    '''
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        try:
            __foreEndListAuth__=dianyingxinxi.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否":
            tablename=session.get("tablename")
            if tablename!="users":
                req_dict['userid']=session.get("params").get("id")

        error= dianyingxinxi.createbyreq(dianyingxinxi, dianyingxinxi, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return jsonify(msg)

# 踩、赞接口
@main_bp.route("/python9532dr50/dianyingxinxi/thumbsup/<id_>", methods=['GET'])
def python9532dr50_dianyingxinxi_thumbsup(id_):
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        id_=int(id_)
        type_=int(req_dict.get("type",0))
        rets=dianyingxinxi.getbyid(dianyingxinxi, dianyingxinxi,id_)

        update_dict={
        "id":id_,
        }
        if type_==1:#赞
            update_dict["thumbsupnum"]=int(rets[0].get('thumbsupnum'))+1
        elif type_==2:#踩
            update_dict["crazilynum"]=int(rets[0].get('crazilynum'))+1
        error = dianyingxinxi.updatebyparams(dianyingxinxi, dianyingxinxi, update_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return jsonify(msg)

# 获取详情信息（后端）
@main_bp.route("/python9532dr50/dianyingxinxi/info/<id_>", methods=['GET'])
def python9532dr50_dianyingxinxi_info(id_):
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}

        data = dianyingxinxi.getbyid(dianyingxinxi, dianyingxinxi, int(id_))
        if len(data)>0:
            msg['data']=data[0]
        #浏览点击次数
        try:
            __browseClick__= dianyingxinxi.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__  and  "clicknum"  in dianyingxinxi.__table__.columns:
            click_dict={"id":int(id_),"clicknum":str(int(data[0].get("clicknum") or 0)+1)}
            ret=dianyingxinxi.updatebyparams(dianyingxinxi,dianyingxinxi,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return jsonify(msg)

# 获取详情信息（前端）
@main_bp.route("/python9532dr50/dianyingxinxi/detail/<id_>", methods=['GET'])
def python9532dr50_dianyingxinxi_detail(id_):
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}

        data = dianyingxinxi.getbyid(dianyingxinxi, dianyingxinxi, int(id_))
        if len(data)>0:
            msg['data']=data[0]

        #浏览点击次数
        try:
            __browseClick__= dianyingxinxi.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__ and "clicknum" in dianyingxinxi.__table__.columns:
            click_dict={"id":int(id_),"clicknum":str(int(data[0].get("clicknum") or 0)+1)}
            ret=dianyingxinxi.updatebyparams(dianyingxinxi,dianyingxinxi,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return jsonify(msg)

# 更新接口
@main_bp.route("/python9532dr50/dianyingxinxi/update", methods=['POST'])
def python9532dr50_dianyingxinxi_update():
    '''
    '''
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        if req_dict.get("mima") and "mima" not in dianyingxinxi.__table__.columns :
            del req_dict["mima"]
        if req_dict.get("password") and "password" not in dianyingxinxi.__table__.columns :
            del req_dict["password"]
        try:
            del req_dict["clicknum"]
        except:
            pass


        error = dianyingxinxi.updatebyparams(dianyingxinxi, dianyingxinxi, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error


        return jsonify(msg)

# 删除接口
@main_bp.route("/python9532dr50/dianyingxinxi/delete", methods=['POST'])
def python9532dr50_dianyingxinxi_delete():
    '''
    '''
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")

        error=dianyingxinxi.delete(
            dianyingxinxi,
            req_dict
        )
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return jsonify(msg)

# 投票接口
@main_bp.route("/python9532dr50/dianyingxinxi/vote/<int:id_>", methods=['POST'])
def python9532dr50_dianyingxinxi_vote(id_):
    '''
    '''
    if request.method == 'POST':
        msg = {"code": normal_code, "msg": "success"}


        data= dianyingxinxi.getbyid(dianyingxinxi, dianyingxinxi, int(id_))
        for i in data:
            votenum=i.get('votenum')
            if votenum!=None:
                params={"id":int(id_),"votenum":votenum+1}
                error=dianyingxinxi.updatebyparams(dianyingxinxi,dianyingxinxi,params)
                if error!=None:
                    msg['code'] = crud_error_code
                    msg['msg'] = error
        return jsonify(msg)


@main_bp.route("/python9532dr50/dianyingxinxi/sectionStat/pingfen", methods=['GET'])
def python9532dr50_dianyingxinxi_sectionStat_pingfen():
    '''
    分段统计接口
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": []}
        where = " where 1=1"
        tablename=session.get("tablename")
        sql = """
            SELECT '四分以下' as pingfen,case when t.四分以下 is null then 0 else t.四分以下 end total
            from 
            (select
            sum(case when pingfen >= 0 and pingfen <= 4 then 1 else 0 end) as 四分以下,            sum(case when pingfen >= 4.1 and pingfen <= 6 then 1 else 0 end) as 四分到六分,            sum(case when pingfen >= 6.1 and pingfen <= 8 then 1 else 0 end) as 六分到八分,            sum(case when pingfen >= 8.1 and pingfen <= 10 then 1 else 0 end) as 八到十分            from dianyingxinxi """ +where+""" ) t union all            SELECT '四分到六分' as pingfen,case when t.四分到六分 is null then 0 else t.四分到六分 end total
            from 
            (select
            sum(case when pingfen >= 0 and pingfen <= 4 then 1 else 0 end) as 四分以下,            sum(case when pingfen >= 4.1 and pingfen <= 6 then 1 else 0 end) as 四分到六分,            sum(case when pingfen >= 6.1 and pingfen <= 8 then 1 else 0 end) as 六分到八分,            sum(case when pingfen >= 8.1 and pingfen <= 10 then 1 else 0 end) as 八到十分            from dianyingxinxi """ +where+""" ) t union all            SELECT '六分到八分' as pingfen,case when t.六分到八分 is null then 0 else t.六分到八分 end total
            from 
            (select
            sum(case when pingfen >= 0 and pingfen <= 4 then 1 else 0 end) as 四分以下,            sum(case when pingfen >= 4.1 and pingfen <= 6 then 1 else 0 end) as 四分到六分,            sum(case when pingfen >= 6.1 and pingfen <= 8 then 1 else 0 end) as 六分到八分,            sum(case when pingfen >= 8.1 and pingfen <= 10 then 1 else 0 end) as 八到十分            from dianyingxinxi """ +where+""" ) t union all            SELECT '八到十分' as pingfen,case when t.八到十分 is null then 0 else t.八到十分 end total
            from 
            (select
            sum(case when pingfen >= 0 and pingfen <= 4 then 1 else 0 end) as 四分以下,            sum(case when pingfen >= 4.1 and pingfen <= 6 then 1 else 0 end) as 四分到六分,            sum(case when pingfen >= 6.1 and pingfen <= 8 then 1 else 0 end) as 六分到八分,            sum(case when pingfen >= 8.1 and pingfen <= 10 then 1 else 0 end) as 八到十分            from dianyingxinxi """ +where+""" ) t  """

        data = db.session.execute(sql)
        data = data.fetchall()
        results = []
        for i in range(len(data)):
            result = {
                'pingfen': decimalEncoder(data[i][0]),
                'total': decimalEncoder(data[i][1])
            }
            results.append(result)
            
        msg['data'] = results
        return jsonify(msg)
@main_bp.route("/python9532dr50/dianyingxinxi/sectionStat/wxs", methods=['GET'])
def python9532dr50_dianyingxinxi_sectionStat_wxs():
    '''
    分段统计接口
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": []}
        where = " where 1=1"
        tablename=session.get("tablename")
        sql = """
            SELECT '二分以下' as wxs,case when t.二分以下 is null then 0 else t.二分以下 end total
            from 
            (select
            sum(case when wxs >= 0 and wxs <= 2 then 1 else 0 end) as 二分以下,            sum(case when wxs >= 2.1 and wxs <= 4 then 1 else 0 end) as 二到4分,            sum(case when wxs >= 4.1 and wxs <= 5 then 1 else 0 end) as 四分到五分            from dianyingxinxi """ +where+""" ) t union all            SELECT '二到4分' as wxs,case when t.二到4分 is null then 0 else t.二到4分 end total
            from 
            (select
            sum(case when wxs >= 0 and wxs <= 2 then 1 else 0 end) as 二分以下,            sum(case when wxs >= 2.1 and wxs <= 4 then 1 else 0 end) as 二到4分,            sum(case when wxs >= 4.1 and wxs <= 5 then 1 else 0 end) as 四分到五分            from dianyingxinxi """ +where+""" ) t union all            SELECT '四分到五分' as wxs,case when t.四分到五分 is null then 0 else t.四分到五分 end total
            from 
            (select
            sum(case when wxs >= 0 and wxs <= 2 then 1 else 0 end) as 二分以下,            sum(case when wxs >= 2.1 and wxs <= 4 then 1 else 0 end) as 二到4分,            sum(case when wxs >= 4.1 and wxs <= 5 then 1 else 0 end) as 四分到五分            from dianyingxinxi """ +where+""" ) t  """

        data = db.session.execute(sql)
        data = data.fetchall()
        results = []
        for i in range(len(data)):
            result = {
                'wxs': decimalEncoder(data[i][0]),
                'total': decimalEncoder(data[i][1])
            }
            results.append(result)
            
        msg['data'] = results
        return jsonify(msg)


# 分组统计接口
@main_bp.route("/python9532dr50/dianyingxinxi/group/<columnName>", methods=['GET'])
def python9532dr50_dianyingxinxi_group(columnName):
    '''
    分组统计接口
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        userinfo = session.get("params")


        msg['data'] = dianyingxinxi.groupbycolumnname(dianyingxinxi,dianyingxinxi,columnName,req_dict)
        msg['data'] = msg['data'][:10]
        msg['data'] = [ {**i,columnName:str(i[columnName])} if columnName in i else i for i in msg['data']]
        json_filename='dianyingxinxi'+f'_group_{columnName}.json'

        where = ' where 1 = 1 '
        sql = "SELECT COUNT(*) AS total, " + columnName + " FROM dianyingxinxi " + where + " GROUP BY " + columnName
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(msg['data'], indent=4, ensure_ascii=False))
        app.executor.submit(upload_to_hdfs, json_filename)
        app.executor.submit(MRMySQLAvg.run)
        return jsonify(msg)

# 按值统计接口
@main_bp.route("/python9532dr50/dianyingxinxi/value/<xColumnName>/<yColumnName>", methods=['GET'])
def python9532dr50_dianyingxinxi_value(xColumnName, yColumnName):
    '''
    按值统计接口,
    {
        "code": 0,
        "data": [
            {
                "total": 10.0,
                "shangpinleibie": "aa"
            },
            {
                "total": 20.0,
                "shangpinleibie": "bb"
            },
            {
                "total": 15.0,
                "shangpinleibie": "cc"
            }
        ]
    }
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = session.get("req_dict")
        userinfo = session.get("params")


        msg['data'] = dianyingxinxi.getvaluebyxycolumnname(dianyingxinxi,dianyingxinxi,xColumnName,yColumnName,req_dict)
        msg['data'] = msg['data'][:10]
        return jsonify(msg)

# 按日期统计接口
@main_bp.route("/python9532dr50/dianyingxinxi/value/<xColumnName>/<yColumnName>/<timeStatType>", methods=['GET'])
def python9532dr50_dianyingxinxi_value_riqi(xColumnName, yColumnName, timeStatType):
    '''
    按日期统计接口
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}

        userinfo = session.get("params")
        where = ' where 1 = 1 '
        sql = ''
        if timeStatType == '日':
            sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName, yColumnName, where, '%Y-%m-%d')

        if timeStatType == '月':
            sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName, yColumnName, where, '%Y-%m')

        if timeStatType == '年':
            sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName, yColumnName, where, '%Y')

        data = db.session.execute(sql)
        data = data.fetchall()
        results = []
        for i in range(len(data)):
            result = {
                xColumnName: decimalEncoder(data[i][0]),
                'total': decimalEncoder(data[i][1])
            }
            results.append(result)
            
        msg['data'] = results
        json_filename='dianyingxinxi'+f'_value_{xColumnName}_{yColumnName}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(results, indent=4, ensure_ascii=False))
        app.executor.submit(upload_to_hdfs, json_filename)
        app.executor.submit(MRMySQLAvg.run)
    return jsonify(msg)

# 按值统计（多）
@main_bp.route("/python9532dr50/dianyingxinxi/valueMul/<xColumnName>", methods=['GET'])
def python9532dr50_dianyingxinxi_valueMul(xColumnName):

    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": []}

        req_dict = session.get("req_dict")
        userinfo = session.get("params")

        where = ' where 1 = 1 '

        for item in req_dict['yColumnNameMul'].split(','):
            sql = "SELECT {0}, sum({1}) AS total FROM dianyingxinxi {2} GROUP BY {0} LIMIT 10".format(xColumnName, item, where)
            L = []
            data = db.session.execute(sql)
            data = data.fetchall() 
            for i in range(len(data)):
                result = {
                    xColumnName: decimalEncoder(data[i][0]),
                    'total': decimalEncoder(data[i][1])
                }
                L.append(result)
            msg['data'].append(L)

        return jsonify(msg)

# 按值统计（多）
@main_bp.route("/python9532dr50/dianyingxinxi/valueMul/<xColumnName>/<timeStatType>", methods=['GET'])
def python9532dr50_dianyingxinxi_valueMul_time(xColumnName):

    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": []}

        req_dict = session.get("req_dict")
        userinfo = session.get("params")
        timeStatType = req_dict['timeStatType']
        where = ' where 1 = 1 '

        for item in req_dict['yColumnNameMul'].split(','):
            sql = ''
            if timeStatType == '日':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d') LIMIT 10".format(xColumnName, item, where, '%Y-%m-%d')

            if timeStatType == '月':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y-%m') LIMIT 10".format(xColumnName, item, where, '%Y-%m')

            if timeStatType == '年':
                sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, sum({1}) total FROM dianyingxinxi {2} GROUP BY DATE_FORMAT({0}, '%Y') LIMIT 10".format(xColumnName, item, where, '%Y')
            L = []
            data = db.session.execute(sql)
            data = data.fetchall() 
            for i in range(len(data)):
                result = {
                    xColumnName: decimalEncoder(data[i][0]),
                    'total': decimalEncoder(data[i][1])
                }
                L.append(result)
            msg['data'].append(L)

        return jsonify(msg)

import math
def cosine_similarity(a, b):
    numerator = sum([a[key] * b[key] for key in a if key in b])
    denominator = math.sqrt(sum([a[key]**2 for key in a])) * math.sqrt(sum([b[key]**2 for key in b]))
    return numerator / denominator

#收藏协同算法
@main_bp.route("/python9532dr50/dianyingxinxi/autoSort2", methods=['GET'])
def python9532dr50_dianyingxinxi_autoSort2():
    if request.method == 'GET':
        user_ratings = {}
        req_dict = session.get("req_dict")
        userinfo = session.get("params")
        sql = "select * from storeup where type = 1 and tablename = 'dianyingxinxi' order by addtime desc"
        data = db.session.execute(sql)
        data_dict = [dict(zip(result.keys(), result)) for result in data.fetchall()]

        for item in data_dict:
            if user_ratings.__contains__(item["userid"]):
                ratings_dict = user_ratings[item["userid"]]
                if ratings_dict.__contains__(item["refid"]):
                    ratings_dict[str(item["refid"])]+=1
                else:
                    ratings_dict[str(item["refid"])]=1
            else:
                user_ratings[item["userid"]] = {
                    str(item["refid"]):1
                }
        sorted_recommended_goods=[]
        try:
            # 计算目标用户与其他用户的相似度
            similarities = {other_user: cosine_similarity(user_ratings[userinfo.get("id")], user_ratings[other_user])
                            for other_user in user_ratings if other_user != userinfo.get("id")}

            # 找到与目标用户最相似的用户
            most_similar_user = sorted(similarities, key=similarities.get, reverse=True)[0]
            # 找到最相似但目标用户未购买过的商品
            recommended_goods = {goods: rating for goods, rating in user_ratings[most_similar_user].items() if
                                 goods not in user_ratings[userinfo.get("id")]}
            # 按评分降序排列推荐
            sorted_recommended_goods = sorted(recommended_goods, key=recommended_goods.get, reverse=True)
        except:
            pass

        L = []
        where = " AND ".join([f"{key} = '{value}'" for key, value in req_dict.items() if key!="page" and key!="limit" and key!="order"and key!="sort"])
        if where:
            sql = f'''SELECT * FROM (SELECT * FROM dianyingxinxi WHERE {where}) AS table1 WHERE id IN ('{"','".join(sorted_recommended_goods)}') union all SELECT * FROM (SELECT * FROM dianyingxinxi WHERE {where}) AS table1 WHERE id NOT IN ('{"','".join(sorted_recommended_goods)}')'''
        else:
            sql ="select * from dianyingxinxi where id in ('%s"%("','").join(sorted_recommended_goods)+"') union all select * from dianyingxinxi where id not in('%s"%("','").join(sorted_recommended_goods)+"')"
        data = db.session.execute(sql)
        data_dict = [dict(zip(result.keys(), result)) for result in data.fetchall()]
        for online_dict in data_dict:
            for key in online_dict:
                if 'datetime.datetime' in str(type(online_dict[key])):
                    online_dict[key] = online_dict[key].strftime(
                        "%Y-%m-%d %H:%M:%S")
                elif 'datetime' in str(type(online_dict[key])):
                    online_dict[key] = online_dict[key].strftime(
                        "%Y-%m-%d %H:%M:%S")
                else:
                    pass
            L.append(online_dict)

        return jsonify({"code": 0, "msg": '',  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":5,"list": L[0:int(req_dict['limit'])]}})


# 总数量
@main_bp.route("/python9532dr50/dianyingxinxi/count", methods=['GET'])
def python9532dr50_dianyingxinxi_count():
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success",  "data": 0}
        req_dict = session.get("req_dict")
        userinfo = session.get("params")


        msg['data']  = dianyingxinxi.count(dianyingxinxi, dianyingxinxi, req_dict)

        return jsonify(msg)

# 统计接口
@main_bp.route("/python9532dr50/dianyingxinxi/remind/<columnName>/<type>", methods=['GET'])  #
def python9532dr50_dianyingxinxi_remind(columnName,type):
    '''
    '''
    if request.method == 'GET':
        msg = {"code": normal_code, 'count': 0}
        # 组合查询参数
        params = session.get("req_dict")
        remindstart = 0
        remindend =9999990
        if int(type)==1:#数字
            if params.get('remindstart') == None and params.get('remindend') != None:
                remindstart = 0
                remindend = int(params['remindend'])
            elif params.get('remindstart') != None and params.get('remindend') == None:
                remindstart = int(params['remindstart'])
                remindend = 999999
            elif params.get('remindstart') == None and params.get('remindend') == None:
                remindstart = 0
                remindend = 999999
            else:
                remindstart = params.get('remindstart')
                remindend =  params.get('remindend')
        elif int(type)==2:#日期
            current_time=int(time.time())
            if params.get('remindstart') == None and params.get('remindend') != None:
                starttime=current_time-60*60*24*365*2
                params['remindstart'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(starttime))
                endtime=current_time+60*60*24*params.get('remindend')
                params['remindend'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endtime))

            elif params.get('remindstart') != None and params.get('remindend') == None:
                starttime= current_time - 60 * 60 * 24 * params.get('remindstart')
                params['remindstart']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(starttime))
                endtime=current_time+60*60*24*365*2
                params['remindend'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endtime))
            elif params.get('remindstart') == None and params.get('remindend') == None:
                starttime = current_time - 60 * 60 * 24 * 365 * 2
                params['remindstart'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(starttime))
                endtime = current_time + 60 * 60 * 24 * 365 * 2
                params['remindend'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endtime))

        data = dianyingxinxi.getbetweenparams(
            dianyingxinxi,
            dianyingxinxi,
            columnName,
            {
                "remindStart": remindstart,
                "remindEnd": remindend
            }
        )

        msg['count'] = len(data)
        return jsonify(msg)

#分类列表
@main_bp.route("/python9532dr50/dianyingxinxi/lists", methods=['GET'])
def python9532dr50_dianyingxinxi_lists():
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": []}
        list,_,_,_,_ = dianyingxinxi.page(dianyingxinxi,dianyingxinxi,{})
        msg['data'] = list
        return jsonify(msg)

# 1. 常量定义
normal_code = 200
crud_error_code = 500  
password_error_code = 401
password_error_code = 401
token_error_code = 402
auth_error_code = 403

# 2. 创建配置模型目录结构
"""
/d:/pj/
    ├── api/
    │   └── models/
    │       ├── __init__.py
    │       └── config_model.py
    └── DY可视化2.py
"""
import logging
import os
import json
import configparser
import time
from datetime import datetime
from flask import Flask, request, jsonify, session
from sqlalchemy import create_engine, Column, Integer, String, Float, func, and_, or_, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建基础类
Base = declarative_base()

# 创建Flask应用
app = Flask(__name__)

# 定义错误码
normal_code = 200
crud_error_code = 500

# 数据库配置
DATABASE = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'database': 'movie_db'
}

try:
    from api.models.dianyingxinxi_model import dianyingxinxi
    from utils.codes import *
    from utils.jwt_auth import Auth
    from configs import configs
    from utils.helper import *
    try:
        from utils.baidubce_api import BaiDuBce
    except ImportError:
        BaiDuBce = None
    from api.models.config_model import config
except ImportError:
    dianyingxinxi = None
    Auth = None
    configs = {}
    BaiDuBce = None
    config = None

# 创建数据库连接
engine = create_engine(f"mysql+pymysql://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}")
DBSession = sessionmaker(bind=engine)

# 1. 常量定义
normal_code = 200
crud_error_code = 500
password_error_code = 401
token_error_code = 402

# 2. 统计总数量
@main_bp.route("/python9532dr50/dianyingxinxi/total", methods=['GET'])
def python9532dr50_dianyingxinxi_count():
    """获取记录总数"""
    try:
        total = db.session.query(Dianyingxinxi).count()
        return jsonify({"code": normal_code, "msg": "success", "data": total})
    except Exception as e:
        return jsonify({"code": crud_error_code, "msg": str(e)})

# 3. 统计提醒
@main_bp.route("/python9532dr50/dianyingxinxi/remind/<columnName>/<type>", methods=['GET'])
def python9532dr50_dianyingxinxi_remind(columnName, type):
    """统计提醒接口"""
    try:
        if type == 'month':
            # 按月统计
            count = db.session.query(Dianyingxinxi).filter(
                extract('month', Dianyingxinxi.addtime) == datetime.now().month
            ).count()
        elif type == 'week':
            # 按周统计
            count = db.session.query(Dianyingxinxi).filter(
                Dianyingxinxi.addtime >= datetime.now() - timedelta(days=7)
            ).count()
        else:
            # 按天统计
            count = db.session.query(Dianyingxinxi).filter(
                cast(Dianyingxinxi.addtime, Date) == date.today()
            ).count()
        
        return jsonify({"code": normal_code, "msg": "success", "data": count})
    except Exception as e:
        return jsonify({"code": crud_error_code, "msg": str(e)})

# 4. 分类列表
@main_bp.route("/python9532dr50/dianyingxinxi/list", methods=['GET'])
def python9532dr50_dianyingxinxi_lists():
    """获取分类列表"""
    try:
        # 获取所有分类
        categories = db.session.query(
            Dianyingxinxi.category
        ).distinct().all()
        
        result = [{"category": cat[0]} for cat in categories if cat[0]]
        return jsonify({
            "code": normal_code,
            "msg": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "code": crud_error_code,
            "msg": str(e),
            "data": []
        })
from datetime import datetime, date, timedelta
from sqlalchemy import extract, cast, Date
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

@main_bp.route("/python9532dr50/dianyingxinxi/sort", methods=['GET'])
def python9532dr50_dianyingxinxi_sort():
    if request.method == 'GET':
        msg = {"code": normal_code, "msg": "success", "data": {}}
        req_dict = request.args.to_dict()
        
        # 根据点击类型设置排序
        browse_click = req_dict.get('browseClick', '')
        if browse_click == '是':
            req_dict['sort'] = 'clicknum'
        elif browse_click == '时长':
            req_dict['sort'] = 'browseduration'
        else:
            req_dict['sort'] = 'clicktime'
            
        # 获取分页数据
        result = dianyingxinxi.page(dianyingxinxi, dianyingxinxi, req_dict)
        msg['data'].update({
            'list': result[0],
            'currPage': result[1],
            'totalPage': result[2],
            'total': result[3],
            'pageSize': result[4]
        })

        return jsonify(msg)

@main_bp.route("/python9532dr50/dianyingxinxi/list", methods=['GET'])
def python9532dr50_dianyingxinxi_list():
    if request.method == 'GET':
        msg = {
            "code": normal_code,
            "msg": "success",
            "data": {
                "currPage": 1,
                "totalPage": 1,
                "total": 1,
                "pageSize": 10,
                "list": []
            }
        }
        
        req_dict = session.get("req_dict", {})
        if 'vipread' in req_dict:
            del req_dict['vipread']
            
        userinfo = session.get("params")