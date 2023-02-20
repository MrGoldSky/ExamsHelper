import sqlite3
from config import TG_BASE_PATH


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
    
    def insert_last_name(self, user_id, last_name):
        con, cur = connect_to_db()
        try:
            cur.execute(f"""UPDATE base
                        SET last_name = '{last_name}'
                        WHERE user_id = {user_id}
                    """)
            
            con.commit()
            con.close()
        except BaseException:
            print("Ошибка заполнения БД (last_name)")
    
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
    def select_status(self, user_id):
        con, cur = connect_to_db()
        try:
            result = cur.execute(f"""SELECT status from base
                        WHERE user_id = {user_id}
                    """).fetchone()[0]
            con.close()
            return result
        except BaseException:
            print("Ошибка заполнения БД (status)")