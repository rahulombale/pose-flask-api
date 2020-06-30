import datetime
import sqlite3

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from resource.instructorpose import CollectInstructor, InstructorBodyData, CollectInstructorInterval
from resource.calorie import Calorie
from resource.exercise import Exercise, ExerciseRegister, Capture
from resource.feedback import Feedback
from resource.record import CalorieRecord, Reward, TimeRecord
from resource.score import Score
from resource.user import UserRegister
from resource.userpose import UserBodyData, CollectUser
from resource.voice import Voice
from resource.weight import Weight
from flask_jwt_extended import create_access_token
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from werkzeug.security import check_password_hash, generate_password_hash
from resource.user import User

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'physio'

jwt = JWTManager(app)


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank")

    def post(self):
        args = Login.parser.parse_args()
        user = User.find_by_username(args['username'])
        if user and check_password_hash(user.password, args['password']):
            expires = datetime.timedelta(days=365)
            status, goal = Login.is_goal_set(args['username'])
            ret = {'access_token': create_access_token(user.username, expires_delta=expires), 'is_goal_set': status, 'goal': goal, "code": 200}
            return ret, 200
        return {"message": "please check the credentials", "code": 401}, 401

    @classmethod
    def is_goal_set(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        username = username
        try:
            query = "SELECT username FROM exercise_record WHERE username=?"
            row_Time = cursor.execute(query, (username,))
            time_result = row_Time.fetchone()
            query = "SELECT username FROM calorie_record WHERE username=?"
            row_Calorie = cursor.execute(query, (username,))
            calorie_result = row_Calorie.fetchone()
            if time_result:
                connection.close()
                return True, "time"
            elif calorie_result:
                connection.close()
                return True, "calorie"
            return False, None
        except:
            return {"message": "internal server error", "code": 501}, 501

    @jwt.user_claims_loader
    def add_claims_to_access_token(self):
        args = Login.parser.parse_args()
        user = User.find_by_username(args['username'])
        return {'username': user.username,
                'age': user.age}


api.add_resource(Exercise, '/exercise')
api.add_resource(Capture, '/capture')
api.add_resource(Feedback, '/feedback')
api.add_resource(ExerciseRegister, '/exercise_register')
api.add_resource(UserRegister, '/register')
api.add_resource(Login, '/login')
api.add_resource(Calorie, '/calorie')
api.add_resource(Voice, '/voice')
api.add_resource(TimeRecord, '/time_record')
api.add_resource(CalorieRecord, '/calorie_record')
api.add_resource(Weight, '/weight')
api.add_resource(Reward, '/reward')
api.add_resource(InstructorBodyData, '/instructorFrame')
api.add_resource(CollectInstructor, '/collectInstructor')
api.add_resource(UserBodyData, '/userFrame')
api.add_resource(CollectUser, '/collectUser')
api.add_resource(CollectInstructorInterval, '/collectInterval')
api.add_resource(Score, '/accuracy_score')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
