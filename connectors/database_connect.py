import pymysql
import datetime


class CupManagementMySQLDB(object):
    def __init__(self):
        self.connection = pymysql.connect(
            host='db',
            user='root',
            password='coferment',
            database='cup_management',
            cursorclass=pymysql.cursors.DictCursor
        )

    def initialize_db(self):
        pass

    def close(self):
        self.cursor.close()
        self.connection.close()

    def execute_sql(self, sql, params=None, fetch=False):
        if self.connection:
            with self.connection.cursor() as self.cursor:
                if params:
                    self.cursor.execute(sql, params)
                else:
                    self.cursor.execute(sql)
            self.connection.commit()
            if fetch:
                return self.cursor.fetchall()
            return self.cursor.lastrowid
        else:
            raise ValueError('DB Connection Closed')