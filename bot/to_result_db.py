from botConfig import RESULT_BASE_PATH
import sqlite3

def connect_to_db():
    try:
        con = sqlite3.connect(RESULT_BASE_PATH)
        cur = con.cursor()
        return con, cur
    except BaseException as e:
        print(e)
        print("Ошибка подключения к БД")


def insert_result(name, surname, learning_class, percent, grade, user_id, question, time_start, time_solve, answers):
    con, cur = connect_to_db()
    try:
        cur.execute(f"""INSERT INTO base(name, surname, class, percent, grade, user_id, question, time_start, time_solve, answers) 
                    VALUES ("{name}", "{surname}", "{learning_class}", {percent}, {grade}, {user_id}, "{question}", "{time_start}", "{time_solve}", "{answers}")
                """)
        
        con.commit()
        con.close()
    except BaseException as e:
        print(e)
        print("Ошибка заполнения БД (result)")


def select_grade(user_id, question):
    con, cur = connect_to_db()
    try:
        grade = cur.execute(f"""SELECT max(grade) from base WHERE user_id = {user_id} AND question = "{question}"
                """).fetchone()[0]
    except BaseException:
        pass
    return grade


def select_percent(user_id, question):
    con, cur = connect_to_db()
    try:
        percent = cur.execute(f"""SELECT max(percent) from base WHERE user_id = {user_id} AND question = "{question}"
            """).fetchone()[0]
    except BaseException:
        print("Ошибка получения результата (percent)")
    return percent


def select_count(user_id, question):
    con, cur = connect_to_db()
    try:
        count = len(cur.execute(f"""SELECT grade, percent from base WHERE user_id = {user_id} AND question = "{question}"
                    """).fetchall())
    except BaseException :
        pass
    return count