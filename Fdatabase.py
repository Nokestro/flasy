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