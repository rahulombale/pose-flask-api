from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
import sqlite3
import json
from flask_jwt_extended import get_jwt_claims
import datetime

from resource.feedback import Feedback


class UserBodyData(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('frame',
                        type=dict,
                        required=True,
                        help="This field cannot be left blank",
                        )
    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    @jwt_required
    def post(self):
        args = UserBodyData.parser.parse_args()
        frame = args['frame']
        exercise_id = args['exercise_id']
        username = get_jwt_claims()["username"]
        date = datetime.datetime.now()

        reps = Feedback.get_user_reps(exercise_id, username)
        exercise_process_status = 0
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "INSERT INTO userpose VALUES (NULL, ?,?,?,?,?,?)"
            cursor.execute(query, (exercise_id, json.dumps(frame), username, date, reps, exercise_process_status))
        except:
            return {"message": "Internal server error", "code": 501}, 501
        connection.commit()
        connection.close()
        return {"message": " record created successfully", "code": 201}, 201


class CollectUser(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    @jwt_required
    def post(self):
        args = CollectUser.parser.parse_args()
        exercise_id = args['exercise_id']
        username = get_jwt_claims()["username"]
        coordinateList = CollectUser.get_User_Points_For_Exp(exercise_id, username)
        return coordinateList, 200

    @classmethod
    def get_User_Points(cls, exercise_id, username):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        processed_status = 0
        query = "SELECT MAX(reps) FROM userpose WHERE exercise_id =? and username=?"
        try:
            result = cursor.execute(query, (exercise_id, username))
        except:
            return {"message": "internal server error", "code": "501"}, 501

        reps = result.fetchone()[0]

        query = "SELECT data FROM userpose WHERE exercise_id =? and username=? and reps=? and processed=? ORDER BY " \
                "date ASC "
        coordinateList = []
        try:
            result = cursor.execute(query, (exercise_id, username, reps, processed_status))
        except:
            return {"message": "internal server error", "code": "501"}, 501

        for row in result.fetchall():
            coordinateList.append(json.loads(row[0]))
        connection.close()
        return coordinateList

    @classmethod
    def get_User_Points_For_Exp(cls, exercise_id, username):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        processed_status = 1
        query = "SELECT MAX(reps) FROM userpose WHERE exercise_id =? and username=?"
        try:
            result = cursor.execute(query, (exercise_id, username))
        except:
            return {"message": "internal server error", "code": "501"}, 501

        reps = result.fetchone()[0]

        query = "SELECT data FROM userpose WHERE exercise_id =? and username=? and reps=? and processed=? ORDER BY " \
                "date ASC "
        coordinateList = []
        try:
            result = cursor.execute(query, (exercise_id, username, reps, processed_status))
        except:
            return {"message": "internal server error", "code": "501"}, 501

        for row in result.fetchall():
            coordinateList.append(json.loads(row[0]))
        connection.close()
        return coordinateList

    @jwt_required
    def delete(self):
        args = CollectUser.parser.parse_args()
        exercise_id = args['exercise_id']
        username = get_jwt_claims()["username"]
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "DELETE FROM userpose WHERE exercise_id =? and username=?"
            cursor.execute(query, (exercise_id, username))
        except:
            return {"message": "Internal server error", "code": 501}, 501
        connection.commit()
        connection.close()
        return {"message": "records deleted successfully", "code": 202}, 202
