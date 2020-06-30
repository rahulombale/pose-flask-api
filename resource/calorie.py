from flask_jwt_extended import jwt_required, get_jwt_claims
from flask_restful import Resource, reqparse
from resource.exercise import Capture
from resource.record import Reward
from resource.weight import Weight


class Calorie(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('time',
                        type=int,
                        required=True,
                        help="This field cannot be left empty")
    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left empty")

    @jwt_required
    def post(self):

        args = Calorie.parser.parse_args()
        username = get_jwt_claims()['username']
        weight = Weight.get_weight(username)
        print("Weight #######", weight)
        exercise_id = args['exercise_id']
        exercise = Capture.get_exercise(exercise_id)
        intensity = exercise['intensity']

        MET_vector = {"Low": 3, "Medium": 6, "High": 8}
        t_min = args['time'] / 60

        try:
            MET = MET_vector.get(intensity, 2)
            wt_kg = weight
            calorie_burn = (t_min * MET * 3.5 * wt_kg) / 200
        except:
            return {"message": "Failed", "code": 501}, 501
        try:
            healthpoints = int(calorie_burn/2) * 5
            Reward.update_reward(exercise_id, healthpoints)
        except:
            return {"message": "internal server error", "code": 501}, 501
        return {"calorie_burn": calorie_burn, "healthpoints": healthpoints, "code": 200}, 200

