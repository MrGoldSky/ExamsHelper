import sqlite3
from bot.botConfig import TG_BASE_PATH


def connect_to_db():
    try:
        con = sqlite3.connect(TG_BASE_PATH)
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        print(e)
        print("Ошибка подключения к БД")

class insert():

    def insert_id(self, user_id):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""INSERT INTO base(user_id)
                            VALUES ({user_id})
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (id)")
    
    def insert_name(self, user_id, name):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""UPDATE base
                        SET name = '{name}'
                        WHERE user_id = {user_id}
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (name)")
    
    def insert_surname(self, user_id, surname):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""UPDATE base
                        SET surname = '{surname}'
                        WHERE user_id = {user_id}
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (surname)")
    
    def insert_class(self, user_id, class_):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""UPDATE base
                        SET class = '{class_}'
                        WHERE user_id = {user_id}
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (class)")
    
    def insert_status(self, user_id, status):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""UPDATE base
                        SET status = {status}
                        WHERE user_id = {user_id}
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (status)")


class select():
    def select_name(self, user_id):
        con, cur = connect_to_db()
        try:
            name = cur.execute(f"""SELECT name from base
                        WHERE user_id = {user_id}
                    """).fetchone()[0]
            con.close()
            return name
        except BaseException as e:
            print("Ошибка получения (name)")


    def select_surname(self, user_id):
        con, cur = connect_to_db()
        try:
            surname = cur.execute(f"""SELECT surname from base
                        WHERE user_id = {user_id}
                    """).fetchone()[0]
            con.close()
            return surname
        except BaseException:
            print("Ошибка получения (surname)")


    def select_class(self, user_id):
        con, cur = connect_to_db()
        try:
            learning_class = cur.execute(f"""SELECT class from base
                        WHERE user_id = {user_id}
                    """).fetchone()[0]
            con.close()
            return learning_class
        except BaseException:
            print("Ошибка получения (class)")