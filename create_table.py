import sqlite3
connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, username text, password text, " \
               "age INTEGER, name text) "
cursor.execute(create_table)

create_table = "CREATE TABLE IF NOT EXISTS exercise (id INTEGER PRIMARY KEY, exercise_name text, " \
               "exercise_type text, intensity text, duration INTEGER, source text, description text)"
cursor.execute(create_table)

create_table = "CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, effort_score text, username text, " \
               "date Date, exercise_id INTEGER) "
cursor.execute(create_table)

create_table = "CREATE TABLE IF NOT EXISTS exercise_record (id INTEGER PRIMARY KEY, username text, " \
               "date Date, exercise_id INTEGER, current_time INTEGER , goal_time INTEGER, today_time INTEGER) "
cursor.execute(create_table)


create_table = "CREATE TABLE IF NOT EXISTS user_data (id INTEGER PRIMARY KEY, username text, " \
               "date Date, weight real) "
cursor.execute(create_table)

create_table = "CREATE TABLE IF NOT EXISTS calorie_record (id INTEGER PRIMARY KEY, username text, " \
               "date Date, exercise_id INTEGER, current_calories INTEGER , goal_calories INTEGER, today_calories INTEGER) "
cursor.execute(create_table)

create_table = "CREATE TABLE IF NOT EXISTS reward (id INTEGER PRIMARY KEY, username text, " \
               "exercise_id INTEGER, total_healthpoints INTEGER) "
cursor.execute(create_table)

create_table = "CREATE TABLE instructor_pose (id INTEGER NOT NULL, exercise_id INTEGER NOT NULL,"\
                "data json NOT NULL,capture_time INTEGER, PRIMARY KEY(id))"
cursor.execute(create_table)

create_table = "CREATE TABLE userpose (id INTEGER NOT NULL, exercise_id INTEGER NOT NULL,"\
                "data json NOT NULL, username TEXT NOT NULL, date date NOT NULL, PRIMARY KEY(id))"
cursor.execute(create_table)

connection.commit()
connection.close()
