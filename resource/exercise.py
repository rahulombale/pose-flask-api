from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_claims
from flask_restful import Resource, reqparse
import sqlite3

from resource.user import User


class ExerciseRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('exercise_name',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")

    parser.add_argument('exercise_type',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")

    parser.add_argument('intensity',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")

    parser.add_argument('duration',
                        type=int,
                        required=True,
                        help="This field cannot be left blank")

    parser.add_argument('source',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")
    parser.add_argument('description',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")

    def post(self):
        args = ExerciseRegister.parser.parse_args()
        # data = request.get_json()

        exercise = {"exercise_name": args['exercise_name'],
                    "exercise_type": args['exercise_type'],
                    "intensity": args['intensity'],
                    "duration": args['duration'],
                    "source": args['source'],
                    "description": args['description']}
        try:
            self.insert(exercise)
        except:
            return {'message': 'An error occurred inserting the item'}, 500  # internal server error

        return exercise, 201

    @classmethod
    def insert(cls, exercise):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO exercise VALUES (NULL,?,?,?,?,?,?)"
        cursor.execute(query, (
            exercise['exercise_name'], exercise['exercise_type'], exercise['intensity'], exercise['duration'],
            exercise['source']), exercise['description'])
        connection.commit()
        connection.close()

    @classmethod
    def get(cls):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM exercise"
        result = cursor.execute(query)
        Exercises = []

        for row in result.fetchall():
            exercise = {"_id": row[0], "exercise_name": row[1], "exercise_type": row[2], "intensity": row[3],
                        "duration": row[4], "source": row[5], "description": row[6]}
            Exercises.append(exercise)
        connection.close()
        return Exercises

    @classmethod
    def senior_excercise(cls, intensity=None):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        if intensity:
            query = "SELECT * FROM exercise WHERE exercise_type=? and intensity=?"
            result = cursor.execute(query, ('senior citizen', intensity))
        else:
            query = "SELECT * FROM exercise WHERE exercise_type=?"
            result = cursor.execute(query, ('senior citizen',))

        Exercises = []

        for row in result.fetchall():
            exercise = {"_id": row[0], "exercise_name": row[1], "exercise_type": row[2], "intensity": row[3],
                        "duration": row[4], "source": row[5], "description": row[6]}
            Exercises.append(exercise)
        connection.close()
        return Exercises

    @classmethod
    def youth_excercise(cls, intensity=None):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        if intensity:
            query = "SELECT * FROM exercise WHERE exercise_type=? and intensity=?"
            result = cursor.execute(query, ('youth citizen', intensity))
        else:
            query = "SELECT * FROM exercise WHERE exercise_type=?"
            result = cursor.execute(query, ('youth citizen',))
        Exercises = []

        for row in result.fetchall():
            exercise = {"_id": row[0], "exercise_name": row[1], "exercise_type": row[2], "intensity": row[3],
                        "duration": row[4], "source": row[5], "description": row[6]}
            Exercises.append(exercise)
        connection.close()
        return Exercises


class Exercise(Resource):

    @jwt_required
    def get(self):
        try:
            exercise_array = ExerciseRegister.get()
            return {"Exercise": exercise_array, "code": 200}, 200
        except:
            return {"message": 'internal server error', "code": 501}, 501


class Capture(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('exercise_id',
                        type=str,
                        required=True,
                        help="This field cannot be left blank",
                        )

    @jwt_required
    def post(self):
        args = Capture.parser.parse_args()
        exercise_id = args['exercise_id']

        if exercise_id:
            exercise = Capture.get_exercise(exercise_id)
            if len(exercise) >= 1:
                return {"exercise": exercise, "code": 200}, 200
        return {"message": "internal server error", "code": 501}, 501

    @classmethod
    def get_exercise(cls, exercise_id):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        exercise = {}
        try:
            query = "SELECT * FROM exercise WHERE id=?"
            result = cursor.execute(query, (exercise_id,))
            row = result.fetchone()
            exercise = {"_id": row[0], "exercise_name": row[1], "exercise_type": row[2], "intensity": row[3],
                        "duration": row[4], "source": row[5], "description": row[6]}
            connection.close()
            return exercise
        except:
            return exercise
