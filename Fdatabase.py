import math
import time
import sqlite3
import re

from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__curs = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__curs.execute(sql)
            res = self.__curs.fetchall()
            if res: return res
        except:
            print("Ошибка вывода из БД")
        return []

    def addPosts(self, title, text, url):
        try:
            self.__curs.execute(f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'")
            res = self.__curs.fetchone()
            if res['count']>0:
                print('Статья с таким URL уже существует')
                return False

            base = url_for('static', filename='images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__curs.execute('INSERT INTO posts VALUES (NULL, ?, ?, ?, ?)', (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи в БД ' + str(e))
            return False

        return True

    def getPost(self, alias):
        try:
            self.__curs.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__curs.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
                print('Ошибка получения статьи из БД ' + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__curs.execute(f'SELECT id, title, url, text FROM posts ORDER BY time DESC')
            res = self.__curs.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения статьи из БД ' + str(e))

        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__curs.execute(f"SElECT COUNT() as 'count' FROM users WHERE email like '{email}'")
            res = self.__curs.fetchone()
            if res['count']>0:
                print('Пользователь с такии email уже существует')
                return False

            tm = math.floor(time.time())
            self.__curs.execute ("INSERT INTO users VALUE (NULL, ?, ?, ?, ?,)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"ошибка добавления в БД: " + str(e))
            return False

        return True


    def getUser(self, user_id):
        try:
            self.__curs.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__curs.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res

        except sqlite3.Error as e:
            print('Ошибка получения данных из БД: '+ str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__curs.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__curs.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res

        except sqlite3.Error as e:
            print('Ошибка получения данных из БД: ' + str(e))

        return False