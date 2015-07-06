# coding:utf-8
__author__ = 'zane'

from settings import *
import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import datetime
class DBPool(object):
    """数据库连接池"""
    #连接池对象
    @staticmethod
    def getConn(dbName):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if not DBPool.poolDict.has_key(dbName):
            pool = PooledDB(creator=MySQLdb, mincached=10 , maxcached=20 ,
                              host=DB_HOST , port=DB_PORT , user=DB_USER , passwd=DB_PWD ,
                              db=dbName,use_unicode=False,charset='utf8',cursorclass=DictCursor)
            DBPool.poolDict[dbName] = pool
        return DBPool.poolDict[dbName].connection()

    @staticmethod
    def getSelectConn(dbName):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if not DBPool.poolSelectDict.has_key(dbName):
            pool = PooledDB(creator=MySQLdb, mincached=1 , maxcached=1 ,
                              host=DB_HOST , port=DB_PORT , user=DB_USER , passwd=DB_PWD ,
                              db=dbName,use_unicode=False,charset='utf8',cursorclass=DictCursor)
            DBPool.poolSelectDict[dbName] = pool
        return DBPool.poolSelectDict[dbName].connection()

DBPool()
class DB(object):
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = Mysql.getConn()
        释放连接对象;conn.close()或del conn
    """

    def __init__(self):
        self.pool = DBPool
        self.sql = ""


    def _create(self, dbName):
        '''从连接池拿连接和指针'''
        # con = self.pool.__getConn(dbName)
        con = self.pool.getConn(dbName)
        cursor = con.cursor()
        return con,cursor

    def _selectCreate(self, dbName):
        '''从连接池拿连接和指针'''
        # con = self.pool.__getConn(dbName)
        con = self.pool.getSelectConn(dbName)
        cursor = con.cursor()
        return con,cursor

    def _close(self, con=None, cursor=None):
        '''关闭连接'''
        try:
            if con:
                con.commit()
                # print '--- DB.con > commit   success'

        except Exception,e:
            msg = ' --- DB.con > commit fail ',e
            print msg

        try:
            if cursor:
                cursor.close()
                # print '--- DB.cursor >  close success'
        except Exception,e:
            msg =  ' --- DB.cursor > closed fail ',e
            print msg
        try:
            if con:
                con.close()
                # print '--- DB.con > close success'

        except Exception,e:
            msg = ' --- DB.con > closed fail ',e
            print msg

    def _query(self, dbName, sql, args=None, fetchAll=True, slave=True):
        '''执行查询语句,并返回结果,推荐直接使用fetchone(),fetchall()'''
        try:
            con,cursor = self._create(dbName)

            cursor.execute(sql,args)
            if fetchAll:
                result =  cursor.fetchall()
            else:
                result = cursor.fetchone()

            return result if result else {} #有无记录返回类型一致 ,以免前端闪退
        except Exception, e:
            msg = '%s >>> dbName=%s sql=%s args=%s'%(e,dbName,sql,args)
            print 'utils-DB-_query: msg=%s' % msg
            return False

        finally:
            self.sql = sql
            self._close(con, cursor)

    def _execute(self, dbName,sql,args=None,multiKey=False):
        '''增 删 改
        @note:涉及连接
        @param multiKey: 是否多主键
        @return:
            -insert返回Id（Insert语句联合主键时候如果没有指定multiKey=True,返回0）
            -其他返回影响行数
        '''
        try:
            con,cursor = self._create(dbName)
            result = cursor.execute(sql,args) #如果是更新直接就是影响行数

            if sql.lower().strip().startswith('insert') and not multiKey:
                return cursor.lastrowid  #如果是插入语句,且单主键,返回lastid
            else:
                return result
        except Exception, e:
            msg = '%s >>> dbName=%s sql=%s args=%s'%(e,dbName,sql,args)
            print 'utils-DB-_execute: msg=%s' % msg
            return False

        finally:
            self.sql = sql
            self._close(con, cursor)

    def _executemany(self, dbName, sql, args):
        '''原有方法
        @note:涉及连接
        '''
        try:
            con,cursor = self._create(dbName)
            result = cursor.executemany(sql, args)

            return result
        except Exception, e:
            msg = '%s >>> dbName=%s sql=%s args=%s'%(e,dbName,sql,args)
            print 'utils-DB-_executemany: msg=%s' % msg
            return False

        finally:
            self.sql = sql
            self._close(con, cursor)

    #================================= 以下方法不涉及连接  ==================================
    def fetchone(self, dbName, sql, args=None):
        '''查询一条记录  @return dict'''
        result = self._query(dbName,sql,args,fetchAll=False)
        return result if result else {} #有无记录返回类型一样 dict


    def fetchall(self, dbName, sql, args=None):
        '''查询所有记录 @return tuple'''
        result = self._query(dbName,sql,args,fetchAll=True)
        return result if result else () #有无记录返回类型一样 tuple



    def out_field(self, dbName, table, field, where='1'):
        '''field是列名,返回一个值'''
        sql = "SELECT %s FROM %s WHERE %s"%(field,table,where)
        row = self.fetchone(dbName,sql)
        if not row:
            return None
        return row.get(field)

    def count(self, dbName, table, where='1'):
        '''获取数量 @return int'''
        return self.out_field(dbName,table,'count(1)',where)

    def out_list(self, dbName, table, field, where='1', distinct=False):
        ''' 查询所有满足条件的多行中的field(有相同或不同) 组成一个列表
            @return list
            @example:
            out_list('billing_record_db','order_goods','order_no','payment_method=%s',True) #获取订单号
        '''
        dfield = "DISTINCT(%s) AS %s"%(field,field) if distinct else field
        sql = "SELECT %s FROM %s WHERE %s"%(dfield,table,where)
        rows = self.fetchall(dbName,sql)
        rlist = []
        for row in rows:
            rlist.append(row.get(field))
        return rlist

    def out_row(self, dbName, table, fields, where='1'):
        '''
            @param fields是一个列表,包含列名,返回一个字典
            @return dict-从数据库中读出的记录。
        '''
        sfield = ",".join(fields) if isinstance(fields, (list, tuple)) else fields
        sql = "SELECT %s FROM %s WHERE %s"%(sfield,table,where)
        row = self.fetchone(dbName,sql)
        return row

    def out_rows(self, dbName, table, fields, where='1'):
        '''
            @param fields是一个列表,包含列名,
            @return tuple-从数据库中读出的记录。
        '''
        sfield = ",".join(fields) if isinstance(fields, (list, tuple)) else fields
        sql = "SELECT %s FROM %s WHERE %s"%(sfield,table,where)
        # print 'sql=%s' % sql
        rows =  self.fetchall(dbName,sql)
        return rows

    def sort(self,rows,order):
        '''排序
        @param rows: ({},{},)
        @para order: ['-order_no','payment_method',] 按订单号降序,支付方式升序   注意:排序的值降序时必须是整数
        '''
        def makekey(dic):
            t = ()
            for o in order:
                if o.startswith('-'):
                    t+=(dic[o[1:]]*-1,)
                else:
                    t+=(dic[o],)
            return t
        rows = sorted(rows, key = makekey, reverse=False)
        return rows

    def insert(self, dbName, table, row, raw=[],replace=False):
        '''单条插入 @return int or False
            @param row: dict
            @param raw: list 不加引号字段 , 已兼容方法类或字段类的   ins['RecordTime']='Now()' ,raw=['RecordTime']
        '''
        fields = []
        values = []
        for k,v in row.iteritems():
            fields.append(k)
            if raw and k in raw or isinstance(v, (int,long,float)):
                values.append(v)
            else:
                v = "'%s'"%self.escape_string(v) if isinstance(v, basestring) else v
                values.append(v)

        action = 'REPLACE' if replace else 'INSERT'
        sql = "%s INTO %s (%s) VALUES (%s)"%(action, table, ",".join(fields), ",".join([str(v) for v in values]) ) #值里有%s的有问题
        return self._execute(dbName,sql)

    def update(self, dbName, table, row, where, raw=[]):
        '''执行更新语句  @return int
        @param raw:不加引号字段   已兼容方法类或字段类的
        @e.g.  ups['cargo_fee_rate']='cargo_fee_rate+0.1',raw=['cargo_fee_rate',]
        '''
        groups = []
        for k,v in row.iteritems():
            if k in raw:
                groups.append("%s=%s"%(k,v))
            else:
                cell = "%s='%s'"%(k,self.escape_string(v)) if isinstance(v, basestring) else "%s=%s"%(k,v)
                groups.append(cell)
        sql = "UPDATE %s SET %s WHERE %s"%(table, ",".join(groups), where)
        return self._execute(dbName,sql)

    def insert_update(self, dbName, table, arr, arr_check):
        '''存在则更新，不存在则插入'''
        where = self.mkWhere(arr_check)
        stat = self.count(dbName,table, where)
        if stat:
            update_arr = dict(list(set(arr.items()) - set(arr_check.items())))
            return self.update(dbName,table,update_arr,where)
        return self.insert(dbName,table,arr)

    def mkWhere(self,wdict):
        '''由字典组成 where语句 {'a':1,'b':'c'} 转成  a=1 AND b='c'  '''
        where = ''
        groups = []
        for k,v in wdict.iteritems():
            cell = "%s='%s'"%(k,self.escape_string(v)) if isinstance(v, basestring) else "%s=%s"%(k,v)
            groups.append(cell)
            where = ' AND '.join(groups)
        return where

    def insertmany(self, dbName, table, rows):
        '''批量插入 rows: [{'id':1,'val':1},{'id':2,'val':2},..] 对应于out_rows() '''
        fields = rows[0].keys()
        values = [row.values() for row in rows] #暂不做值的escape_string
        vlist = ',%s'*len(fields)
        sql = 'INSERT INTO %s (%s) VALUES(%s)'%(table, ','.join(fields), vlist[1:])
        return self._executemany(dbName,sql,values)


    def insertmanynew(self, dbName, table, rows, raw=[]):
        '''批量插入 rows: [{'id':1,'val':1},{'id':2,'val':2},..] 对应于out_rows() '''

        for row in rows:
            for k,v in row.iteritems():
                if isinstance(v, (datetime.datetime,datetime.date,datetime.time)):
                    v = v.strftime('%Y-%m-%d %H:%M:%S')
                    v = "'%s'"%v
                elif raw and k in raw or isinstance(v, (int,long,float)):
                    continue
                elif isinstance(v, basestring):
                    v = "'%s'"%self.escape_string(v)
                elif v is None:
                    v = "''"

                row[k] = v

        result = 0 #结果
        tLength = len(rows) #个数
        tMax = 5000 #最大个数
        if tLength>tMax:
            num = tLength / tMax
            for index in range(num+1):
                newRows = rows[index*tMax:(index+1)*tMax]
                if newRows:
                    sql = self.getInsertManySql(table, newRows)
                    result += (self._execute(dbName,sql,multiKey=True) or 0)
        else:
            sql = self.getInsertManySql(table, rows)
            result = self._execute(dbName,sql,multiKey=True)
        return result

    def getInsertManySql(self,table,rows):
        '''获取insertmany sql语气'''
        fields = rows[0].keys()
        sql = 'INSERT INTO %s (%s) VALUES '%(table, ','.join(fields))
        values = []
        for row in rows:
            value = "(" + ",".join([str(v) for v in row.values()]) + ")"
            values.append(value)
        sql += ",".join(values)
        return sql

    def updatemany(self, dbName, table, info, where):
        '''一次更新多条记录 谨用
        @param table: 表名
        @param where: 条件(可能跟要更新的内容有关，暂自行构造 )
        @example:
        #单字段更新 (常用)
        info = ('field1','field2',{when1:then1,when2:then2,..},'field1') //最后元素缺省为第一个元素
        #说明:Info会组成  SET 'field1' = CASE 'field2' When k Then v.. ELSE 'field1' END
        #多单段更新 (少见)
        info = [('field1','field2',{1:2,2:3,3:4,4:5}), ('val3','val4',{1:0,2:1,3:2},'val1')]
        where = 'id in (1,2,3,4)'
        @note: 如果where中条件包含 又没有给出WHEN THEN的值 就会改为ELSE的值,如果没有给出ELSE的值便是0或空
        @remark: 已使用UPDATE good SET price = CASE goodId WHEN 1001 THEN price+57018 WHEN 1002..
        '''
        assert isinstance(info, (list,tuple))

        if isinstance(info,tuple):
            info = [info]
        sql = 'UPDATE %s SET'%table
        for row in info:
            sql += ' %s = CASE %s' % (row[0], row[1])
            for k,v in row[2].iteritems():
                sql += ' WHEN %s THEN %s' % (k,v)
            elsevalue = row[3] if len(row)>3 else row[0] #暂只支持字段或整数- 不支持字符串 因为无引号
            sql += ' ELSE %s' % elsevalue
            sql += ' END,' #如果where中有包含 但又没给出when then则会变为0, 如果这种情况用ELSE 原字段 END
        sql = sql.strip(',') + ' WHERE %s'%where
        return self._execute(dbName,sql)

    def delete(self, dbName, table,where):
        '''删除记录 '''
        sql = "DELETE FROM %s WHERE %s"%(table,where)
        return self._execute(dbName,sql)

    def inWhere(self,field,inList,notIn=False,symbol=False):
        '''
            @param field: 字段
            @param inList: 列表
            @param symbol: 是否有引号
            @return string 条件字符串,用于构造条件
            @example:
            ('id',[1,2,3])  >> id in ('1','2','3') or id in (1,2,3)
            ('Name',['a','b','c'])  >> Name in ('a','b','c')
        '''
        assert isinstance(field, str)
        assert isinstance(inList, (list,tuple))
        if not inList: #对空列表特殊处理
            inList = ['@']
            symbol=True
        inList = [str(cell) for cell in inList]
        notSign = ' NOT' if notIn else ''
        if symbol:
            where = field+notSign+" IN ('"+str.join("','",inList)+"')"
        else:
            where = field+notSign+" IN ("+str.join(",",inList)+")"

        return where

    def escape_string(self,s):
        '''转义逃脱sql中的特殊字符'''
        return MySQLdb.escape_string(s)