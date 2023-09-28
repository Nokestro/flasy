import math
import time
import sqlite3


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

    def addPosts(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__curs.execute('INSERT INTO posts VALUES (NULL, ?, ?, ?)', (title, text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи в БД ' + str(e))
            return False

        return True

    def getPost(self, postId):
        try:
            self.__curs.execute(f'SELECT title, text FROM posts WHERE id == {postId} LIMIT 1')
            res = self.__curs.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
                print('Ошибка получения статьи из БД ' + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__curs.execute(f'SELECT id, title, text FROM posts ORDER BY time DESC')
            res = self.__curs.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print('Ошибка получения статьи из БД ' + str(e))

        return []