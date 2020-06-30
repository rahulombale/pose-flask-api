import sqlite3
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash
from resource.record import Reward
from resource.weight import Weight


class User:
    def __init__(self, username, password, weight, age, first_name, last_name, email):
        self.username = username
        self.password = password
        self.weight = weight
        self.age = age
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        select = 'SELECT username, password, weight, age, first_name, last_name, email FROM user WHERE username = ?'
        result = cursor.execute(select, (username,))
        row = result.fetchone()
        if row:
            user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        else:
            user = None
        connection.close()
        return user

    @classmethod
    def find_by_id(cls, _id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        select = 'SELECT * FROM user WHERE id = ?'

        result = cursor.execute(select, (_id,))
        row = result.fetchone()
        if row:
            # user = cls(row[0], row[1], row[2])
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')
    parser.add_argument('password',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')
    parser.add_argument('age',
                        required=True,
                        type=int,
                        help='this field cannot be left empty')

    parser.add_argument('first_name',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')

    parser.add_argument('last_name',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')

    parser.add_argument('weight',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')

    parser.add_argument('email',
                        required=True,
                        type=str,
                        help='this field cannot be left empty')

    def post(self):
        data = UserRegister.parser.parse_args()
        password = generate_password_hash(data['password'], "sha256")
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        if User.find_by_username(data['username']):
            return {'message': 'The user_name {} is already exist'.format(data['username']), "code": 400}, 400

        query = "INSERT INTO user VALUES (?,?,?,?,?,?,?)"
        try:
            cursor.execute(query, (data['username'], data['first_name'], data['last_name'], password, data['age'], data['weight'], data['email']))
        except:
            return {"message": "User not created successfully", "code": 501}, 501
        connection.commit()
        connection.close()
        Weight.insert_weight(data['weight'], data['username'])
        Reward.create_Reward(data['username'])
        return {"message": "User created  successfully.", "code": 201}, 201
