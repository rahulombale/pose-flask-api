from flask_restful import Resource, reqparse
import sqlite3
import json


class InstructorBodyData(Resource):
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

    def post(self):
        args = InstructorBodyData.parser.parse_args()
        frame = args['frame']
        captureTime = args['frame']['currentTime']
        exercise_id = args['exercise_id']

        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "INSERT INTO instructor_pose VALUES (NULL,?,?,?)"
            cursor.execute(query, (exercise_id, json.dumps(frame), int(captureTime)))
        except:
            return {"message": "Internal server error", "code": 501}, 501
        connection.commit()
        connection.close()
        return {"message": " record created successfully", "code": 201}, 201


class CollectInstructor(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    def post(self):
        args = CollectInstructor.parser.parse_args()
        exercise_id = args['exercise_id']
        coordinateList = CollectInstructor.get_instructor_points(exercise_id)
        return coordinateList, 200

    @classmethod
    def get_instructor_points(cls, exercise_id):
        coordinateList = []
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        query = "SELECT data FROM instructor_pose WHERE exercise_id =?"

        try:
            result = cursor.execute(query, (exercise_id,))
        except:
            return {"message": "internal server error", "code": 501}, 501

        for row in result.fetchall():
            coordinateList.append(json.loads(row[0]))
        connection.close()
        return  coordinateList

    def delete(self):
        args = CollectInstructor.parser.parse_args()
        exercise_id = args['exercise_id']
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "DELETE FROM instructor_pose WHERE exercise_id =?"
            cursor.execute(query, (exercise_id,))
        except:
            return {"message": "Internal server error", "code": 501}, 501
        connection.commit()
        connection.close()
        return {"message": "records deleted successfully", "code": 202}, 202


class CollectInstructorInterval(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    def post(self):
        args = CollectInstructorInterval.parser.parse_args()
        exercise_id = args['exercise_id']
        intervalList = []
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        query = "SELECT capture_time FROM instructor_pose WHERE exercise_id =?"

        try:
            result = cursor.execute(query, (exercise_id,))
        except:
            return {"message": "internal server error", "code": 501}, 501

        for row in result.fetchall():
            intervalList.append(row[0])
        connection.close()
        return {"interval": intervalList, "code": 201}, 201
