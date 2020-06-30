from flask import jsonify
from flask_jwt_extended import get_jwt_claims, jwt_required
from flask_restful import Resource, reqparse
import sqlite3
import datetime


class TimeRecord(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('goal_time',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('current_time',
                            type=int,
                            required=True,
                            help="This field cannot be left blank",
                            )

    put_parser.add_argument('exercise_id',
                            type=int,
                            required=True,
                            help="This field cannot be left blank",
                            )

    @jwt_required
    def post(self):
        args = TimeRecord.parser.parse_args()
        current_time = 0
        exercise_id = 0
        today_time = 0
        goal_time = args['goal_time']
        username = get_jwt_claims()['username']
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        try:
            query = "SELECT username FROM exercise_record WHERE username=?"
            result = cursor.execute(query, (username,))
            if result.fetchone():
                query = "UPDATE exercise_record SET date =?, goal_time =? WHERE username = ? "
                cursor.execute(query, (datetime.datetime.today(), goal_time, username))
                connection.commit()
                connection.close()
                return {"message": "goal updated successfully", "code": 201}, 201
        except:
            return {"message": "internal server error", "code": 501}, 501

        try:
            query = "INSERT INTO exercise_record VALUES(NULL,?,?,?,?,?,?)"
            cursor.execute(query,
                           (username, datetime.datetime.today(), exercise_id, current_time, goal_time, today_time))
            connection.commit()
            connection.close()
            return {"message": "user exercise data stored successfully", "code": 201}, 201
        except:
            return {"message": "internal server error", "code": 501}, 501

    @jwt_required
    def put(self):
        args = TimeRecord.put_parser.parse_args()

        username = get_jwt_claims()['username']
        record = TimeRecord.get_record(username)
        goal_time = record['goal_time']
        today_time = args['current_time']
        current_time = record['current_time']

        new_current_time = current_time + today_time

        exercise_id = args['exercise_id']
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        try:
            query = "UPDATE exercise_record SET date =?, exercise_id =?, current_time =?, today_time=? WHERE username " \
                    "= ? "
            cursor.execute(query, (datetime.datetime.today(), exercise_id, new_current_time, today_time, username))
            connection.commit()
            connection.close()
            return {"message": "user exercise data updated successfully", "code": 201}, 201
        except:
            return {"message": "internal server error", "code": 501}, 501

    @jwt_required
    def get(self):
        username = get_jwt_claims()['username']
        # try:
        record = TimeRecord.get_record(username)
        return {"record": record, "code": 200}, 200
        # except:
        #     return {"message": "internal server error", "code": 501}, 501

    @classmethod
    def get_record(cls, username):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM exercise_record WHERE username =? ORDER BY date DESC limit 1 "
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        remaining_time = row[5] - row[4]
        record = {"id": row[0],
                  "username": row[1],
                  "date": row[2],
                  "exercise_id": row[3],
                  "current_time": row[4],
                  "goal_time": row[5],
                  "today_time": row[6],
                  "remaining_time": remaining_time}
        connection.close()
        return record


class CalorieRecord(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('goal_calories',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('current_calories',
                            type=int,
                            required=True,
                            help="This field cannot be left blank",
                            )

    put_parser.add_argument('exercise_id',
                            type=int,
                            required=True,
                            help="This field cannot be left blank",
                            )

    @jwt_required
    def post(self):
        args = CalorieRecord.parser.parse_args()
        current_calories = 0
        exercise_id = 0
        today_calorie = 0
        goal_calories = args['goal_calories']
        username = get_jwt_claims()['username']

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        try:
            query = "SELECT username FROM calorie_record WHERE username=?"
            result = cursor.execute(query, (username,))
            if result.fetchone():
                query = "UPDATE calorie_record SET date =?, goal_calories =? WHERE username = ? "
                cursor.execute(query, (datetime.datetime.today(), goal_calories, username))
                connection.commit()
                connection.close()
                return {"message": "goal updated successfully", "code": 201}, 201
        except:
            return {"message": "internal server error", "code": 501}, 501
        try:
            query = "INSERT INTO calorie_record VALUES(NULL,?,?,?,?,?,?)"
            cursor.execute(query, (
                username, datetime.datetime.today(), exercise_id, current_calories, goal_calories, today_calorie))
            connection.commit()
            connection.close()
            return {"message": "user exercise data stored successfully", "code": 201}, 201
        except:
            return {"message": "internal server error", "code": 501}, 501

    @jwt_required
    def put(self):
        args = CalorieRecord.put_parser.parse_args()
        today_calories = args['current_calories']
        username = get_jwt_claims()['username']
        record = CalorieRecord.get_record(username)
        goal_calories = record['goal_calories']
        current_calories = record['current_calories']
        new_current_calories = current_calories + today_calories

        exercise_id = args['exercise_id']
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        try:
            query = "UPDATE calorie_record SET date =?, exercise_id =?, current_calories =?, today_calories=? WHERE " \
                    "username = ? "
            cursor.execute(query,
                           (datetime.datetime.today(), exercise_id, new_current_calories, today_calories, username))
            connection.commit()
            connection.close()
            return {"message": "user calories data updated successfully", "code": 204}, 204
        except:
            return {"message": "internal server error", "code": 501}, 501

    @jwt_required
    def get(self):
        username = get_jwt_claims()['username']
        try:
            record = CalorieRecord.get_record(username)
            return {"record": record, "code": 200}, 200
        except:
            return {"message": "internal server error", "code": 501}, 501

    @classmethod
    def get_record(cls, username):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM calorie_record WHERE username =? ORDER BY date DESC limit 1"
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        remaining_calories = row[5] - row[4]
        record = {"id": row[0],
                  "username": row[1],
                  "date": row[2],
                  "exercise_id": row[3],
                  "current_calories": row[4],
                  "goal_calories": row[5],
                  "today_calories": row[6],
                  "remaining_calories": remaining_calories}
        connection.close()
        return record


class Reward(Resource):

    @classmethod
    def update_reward(cls, exercise_id, healthpoints):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        username = get_jwt_claims()['username']
        record = Reward.get_healthpoint(username)
        current_healthpoint = record['total_healthpoint']
        total_healthpoint = current_healthpoint + healthpoints
        query = "UPDATE reward SET exercise_id =?, total_healthpoints=? WHERE username=?"
        cursor.execute(query, (exercise_id, total_healthpoint, username))
        connection.commit()
        connection.close()

    @jwt_required
    def get(self):
        username = get_jwt_claims()['username']
        try:
            record = Reward.get_healthpoint(username)
            if len(record) >= 1:
                return record, 200
        except:
            return {"message": "internal server error", "code": 501}, 501

    @classmethod
    def get_healthpoint(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        username = get_jwt_claims()['username']
        query = "SELECT total_healthpoints FROM reward where username=?"
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        record = {'total_healthpoint': row[0], "code": 200}
        connection.close()
        return record

    @classmethod
    def create_Reward(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        exercise_id = 0
        total_healthpoints = 0
        try:
            query = "INSERT INTO reward VALUES(NULL,?,?,?)"
            cursor.execute(query, (username, exercise_id, total_healthpoints))
            connection.commit()
            connection.close()
        except:
            return {"message": "internal server error", "code": 501}, 501
