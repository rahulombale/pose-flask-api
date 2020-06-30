'''
This module is responsible for the calculating the accuracy score of the exercise.
The _get_score(..) method is responsible for accuracy logic

step1: Both leg wide exercise (horizontal) -> logic based on ankle points (x- axis)
step2: Both hands wide exercise (horizontal) ->  logic based on elbow points (x- axis)
step4: Both leg vertical exercise ->  logic based on ankle points (x- axis)
        both leg should be in fix tolerance margin, inside the shoulder points
step5: Both hands vertical move (stretch video 8 to 15 sec and 1:30 to 1:47 sec ) on (x-axis)
step6: Skipping jump logic -> logic based on knee points (y- axis)
step7 -second half -> random jumps are detected here using (x- axis) of knee
step8: Squat exercise of sports sg, where distance between shoulder and knee point should be less means, user is doing squats.
@Author: Rahul Ombale
'''

import datetime

from flask_restful import Resource, reqparse
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
from flask_jwt_extended import jwt_required, get_jwt_claims
from resource.feedback import Feedback
from resource.userpose import CollectUser
import sqlite3
from scipy import stats
import random
from collections import defaultdict


class Score(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('exercise_id',
                        type=int,
                        required=True,
                        help="This field cannot be left blank",
                        )

    parser.add_argument('Authorization', location='headers')

    @jwt_required
    def post(self):
        args = Score.parser.parse_args()
        exercise_id = args['exercise_id']
        username = get_jwt_claims()["username"]
        date = datetime.datetime.now()
        try:
            user_json = CollectUser.get_User_Points(exercise_id, username)
        except Exception as e:
            return {'exception': str(e) + ' get_user_data', "code": 501}, 501

        try:
            user_df = Score._create_dataframe(user_json)
        except Exception as e:
            return {'exception': str(e) + ' create_dataframe', "code": 501}, 501

        try:
            accuracy_score = Score._get_accuracy_score(user_df, exercise_id)
            print("######accuracy_score", accuracy_score)
        except Exception as e:
            return {'exception': str(e) + ' get_accuracy_score', "code": 501}, 501

        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        try:
            query = "INSERT INTO score VALUES (NULL, ?,?,?,?)"
            cursor.execute(query, (username, exercise_id, date, accuracy_score))
        except Exception as e:
            return {'exception': str(e) + ' score input error', "code": 501}, 501
        connection.commit()
        connection.close()

        processed_status = 1
        reps = Feedback.get_user_reps(exercise_id, username)
        Score.update_exercise_processed_status(processed_status, username, exercise_id, reps)

        return {"accuracy_score": accuracy_score, "code": 200}, 200

    @classmethod
    def update_exercise_processed_status(cls, processed_status, username, exercise_id, reps):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE userpose SET processed =? WHERE username=? and exercise_id =? and reps=?"

        try:
            cursor.execute(query, (processed_status, username, exercise_id, reps))
            connection.commit()
        except Exception as e:
            return {'exception': str(e) + ' processed_status update error at feedback', "code": 501}, 501
        connection.close()

    @classmethod
    def _create_dataframe(cls, json_data):
        main_df_list = []
        parts = ['leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist', 'leftHip',
                 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle']
        length = len(json_data)
        for i in range(length):
            df_list = []
            df = json_normalize(json_data[i]['co-ordinates']['keypoints'])
            df = df.set_index('part')
            record_df = pd.DataFrame({'captureTime': [int(json_data[i]['currentTime'])]
                                      })
            df_list.append(record_df)
            for part in parts:
                temp_df = pd.DataFrame({'{}_x'.format(part): [df.loc[part]['position.x']],
                                        '{}_y'.format(part): [df.loc[part]['position.y']],
                                        '{}_score'.format(part): [df.loc[part]['score']]
                                        })
                df_list.append(temp_df)

            new_df = pd.concat(df_list, axis=1)
            main_df_list.append(new_df)
        main_df = pd.concat(main_df_list)
        main_df.index = np.arange(0, main_df.shape[0])
        return main_df.round()

    @classmethod
    def _get_start_end(cls, df, pose):
        df = df[df['pose'] == pose]
        minTime = df['capture_time'].min()
        maxTime = df['capture_time'].max()
        step = df.iloc[0]['step']
        return minTime, maxTime, step

    @classmethod
    def ankle_movement(cls, leftAnkle_x, leftShoulder_x, rightAnkle_x, rightShoulder_x, shoulderDistance):
        if leftAnkle_x < leftShoulder_x:
            legDistance = leftShoulder_x - leftAnkle_x
            if legDistance > shoulderDistance:
                legDistance = legDistance - shoulderDistance
                accuracy = (legDistance / shoulderDistance) * 100
                normalize_fact = (accuracy % 100) * 100
                accuracy = accuracy - normalize_fact
                return np.ceil(accuracy)
            accuracy = (legDistance / shoulderDistance) * 100
            return np.ceil(accuracy)

        if rightAnkle_x > rightShoulder_x:
            legDistance = rightAnkle_x - rightShoulder_x
            if legDistance > shoulderDistance:
                legDistance = legDistance - shoulderDistance
                accuracy = (legDistance / shoulderDistance) * 100
                normalize_fact = (accuracy % 100) * 100
                accuracy = accuracy - normalize_fact
                return np.ceil(accuracy)
            accuracy = (legDistance / shoulderDistance) * 100
            return np.ceil(accuracy)

    @classmethod
    def left_elbow_movement(cls, leftElbow_x, leftShoulder_x, shoulderDistance):
        shoulderDistance = np.round(shoulderDistance / 1.6)  # elbow out distance ratio maintain

        elbowDistance = leftShoulder_x - leftElbow_x
        if elbowDistance > shoulderDistance:
            elbowDistance = elbowDistance - shoulderDistance
            accuracy = (elbowDistance / shoulderDistance) * 100
            normalize_fact = (accuracy % 100) * 100
            accuracy = accuracy - normalize_fact
            return accuracy
        accuracy = (elbowDistance / shoulderDistance) * 100
        return accuracy

    @classmethod
    def right_elbow_movement(cls, rightShoulder_x, rightElbow_x, shoulderDistance):
        shoulderDistance = np.round(shoulderDistance / 1.6)  # elbow out distance ratio maintain

        elbowDistance = rightElbow_x - rightShoulder_x
        if elbowDistance > shoulderDistance:
            elbowDistance = elbowDistance - shoulderDistance
            accuracy = (elbowDistance / shoulderDistance) * 100
            normalize_fact = (accuracy % 100) * 100
            accuracy = accuracy - normalize_fact
            return accuracy
        accuracy = (elbowDistance / shoulderDistance) * 100
        return accuracy

    @classmethod
    def left_ankle_movement_vertical(cls, leftAnkle_x, leftShoulder_x, shoulderDistance):
        shoulderDistance = np.round(shoulderDistance / 2.4)  # elbow out distance ratio maintain

        if leftAnkle_x > leftShoulder_x:
            legDistance = leftAnkle_x - leftShoulder_x
            if legDistance > shoulderDistance:
                legDistance = legDistance - shoulderDistance
                accuracy = (legDistance / shoulderDistance) * 100
                normalize_fact = (accuracy % 100) * 100
                accuracy = accuracy - normalize_fact
                return accuracy
            accuracy = (legDistance / shoulderDistance) * 100
            return accuracy
        else:
            return 0

    @classmethod
    def right_ankle_movement_vertical(cls, rightAnkle_x, rightShoulder_x, shoulderDistance):
        shoulderDistance = np.round(shoulderDistance / 2.4)  # elbow out distance ratio maintain
        if rightShoulder_x > rightAnkle_x:
            legDistance = rightShoulder_x - rightAnkle_x
            if legDistance > shoulderDistance:
                legDistance = legDistance - shoulderDistance
                accuracy = (legDistance / shoulderDistance) * 100
                normalize_fact = (accuracy % 100) * 100
                accuracy = accuracy - normalize_fact
                return accuracy
            accuracy = (legDistance / shoulderDistance) * 100
            return accuracy
        else:
            return 0

    @classmethod
    def left_elbow_movement_vertical(cls, leftElbow_x, leftShoulder_x, shoulderDistance,exercise_id=0):
        shoulderDistance = np.round(shoulderDistance / 2.6)  # elbow out distance ratio maintain
        # if exercise_id == 4:
        #     shoulderDistance = np.round(shoulderDistance / 2)
        elbowDistance = leftShoulder_x - leftElbow_x
        if elbowDistance > shoulderDistance:
            return 0
        return 100

    @classmethod
    def right_elbow_movement_vertical(cls, rightShoulder_x, rightElbow_x, shoulderDistance, exercise_id=0):
        shoulderDistance = np.round(shoulderDistance / 2.6)  # elbow out distance ratio maintain
        # if exercise_id == 4:
        #     shoulderDistance = np.round(shoulderDistance / 2)
        elbowDistance = rightElbow_x - rightShoulder_x
        if elbowDistance > shoulderDistance:
            return 0
        return 100

    @classmethod
    def jump_accuracy(cls, leftKnee_y, kneeMax):
        instructor_accuracy = 15
        user_accuracy = ((kneeMax - leftKnee_y) / kneeMax) * 100
        accuracy = (user_accuracy / instructor_accuracy) * 100
        if accuracy > 80:
            return 100
        elif accuracy > 60:
            return 80
        else:
            return accuracy

    @classmethod
    def get_shoulderDistance(cls, df):
        df['shoulderDist'] = df['rightShoulder_x'] - df['leftShoulder_x']
        shoulderDistance = np.ceil(np.average(df['shoulderDist']))
        return shoulderDistance

    @classmethod
    def knee_bend_accuracy(cls, left_knee_diff, leftKnee_y):
        # 42% is is resting position distance between the shoulder and knee points Y axis
        accuracy = np.abs(((left_knee_diff / leftKnee_y) * 100) - 100)
        if accuracy > 70:
            return 100
        elif accuracy > 60:
            return 80
        return accuracy

    @classmethod
    def _get_score(cls, min_time, max_time, step, df, sample, exercise_id):
        accuracy_list = []
        accuracy_dict = defaultdict(lambda: "empty")
        shoulderDistance = Score.get_shoulderDistance(df)
        if 'step1' in step:

            minTime = min_time
            maxTime = max_time
            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftShoulder_x', 'leftAnkle_x', 'rightAnkle_x', 'rightShoulder_x']]
            data['ankleMovement'] = data[['leftAnkle_x', 'leftShoulder_x', 'rightAnkle_x', 'rightShoulder_x']].apply(
                lambda x: Score.ankle_movement(x[0], x[1], x[2], x[3], shoulderDistance), axis=1)
            try:
                accuracy = np.average(data.nlargest(sample, ['ankleMovement'])['ankleMovement'])
                if accuracy <= 0:
                    accuracy = 0
            except:
                accuracy = 0
            accuracy_list.append(accuracy)

        if 'step2' in step or 'step3' in step:
            minTime = min_time
            maxTime = max_time
            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['leftElbow_x', 'leftShoulder_x', 'rightShoulder_x', 'rightElbow_x']]
            data['leftElbowMovement'] = data[['leftElbow_x', 'leftShoulder_x']].apply(
                lambda x: Score.left_elbow_movement(x[0], x[1], shoulderDistance), axis=1)
            data['rightElbowMovement'] = data[['rightShoulder_x', 'rightElbow_x']].apply(
                lambda x: Score.right_elbow_movement(x[0], x[1], shoulderDistance), axis=1)
            data = pd.concat([data['leftElbowMovement'], data['rightElbowMovement']], axis=0)
            try:
                accuracy = np.average(data.nlargest(sample))
            except:
                accuracy = 0
            accuracy_list.append(accuracy)

        if 'step5' in step:
            minTime = min_time
            maxTime = max_time
            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftElbow_x', 'leftShoulder_x', 'rightShoulder_x', 'rightElbow_x']]
            data['leftElbowMovement_vertical'] = data[['leftElbow_x', 'leftShoulder_x']].apply(
                lambda x: Score.left_elbow_movement_vertical(x[0], x[1], shoulderDistance, exercise_id), axis=1)
            data['rightElbowMovement_vertical'] = data[['rightShoulder_x', 'rightElbow_x']].apply(
                lambda x: Score.right_elbow_movement_vertical(x[0], x[1], shoulderDistance, exercise_id), axis=1)
            accuracy = np.round(stats.mode(
                pd.concat([data['leftElbowMovement_vertical'], data['rightElbowMovement_vertical']], axis=0))[0][0])
            if accuracy == 0:
                accuracy = 0.01
                accuracy_list.append(accuracy)
                accuracy_dict["step5"] = accuracy

        if 'step4' in step:
            minTime = min_time
            maxTime = max_time
            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftShoulder_x', 'leftAnkle_x', 'rightAnkle_x', 'rightShoulder_x']]
            data['leftAnkleMovement_vertical'] = data[['leftAnkle_x', 'leftShoulder_x']].apply(
                lambda x: Score.left_ankle_movement_vertical(x[0], x[1], shoulderDistance), axis=1)
            data['rightAnkleMovement_vertical'] = data[['rightAnkle_x', 'rightShoulder_x']].apply(
                lambda x: Score.right_ankle_movement_vertical(x[0], x[1], shoulderDistance), axis=1)
            data = pd.concat([data['leftAnkleMovement_vertical'], data['rightAnkleMovement_vertical']], axis=0)

            try:
                accuracy = np.average(data.nlargest(sample))
            except:
                accuracy = 0
            accuracy_list.append(accuracy)

        if 'step6' in step:
            minTime = min_time
            maxTime = max_time
            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftKnee_y', 'rightKnee_y']]
            leftkneeMin = data['leftKnee_y'].min()
            leftkneeMax = data['leftKnee_y'].max()

            rightkneeMin = data['rightKnee_y'].min()
            rightkneeMax = data['rightKnee_y'].max()

            left_jumpDistance = np.abs(np.average(data['leftKnee_y']) - leftkneeMin)
            right_jumpDistance = np.abs(np.average(data['rightKnee_y']) - rightkneeMin)
            if left_jumpDistance <= 10:
                # user has not jumped
                accuracy = 0
            elif right_jumpDistance <= 10:
                accuracy = 0
            else:
                data['jump_accuracy'] = data[['leftKnee_y']].apply(lambda x: Score.jump_accuracy(x[0], rightkneeMax), axis=1)
                try:
                    accuracy = np.average(data.nlargest(3, ['jump_accuracy'])['jump_accuracy'])
                except:
                    accuracy = 0

            accuracy_list.append(accuracy)
            accuracy_dict["step6"] = accuracy

            # step 7 for random dance checking x of the knee
        if 'step7' in step:

            # skipping
            minTime = min_time
            maxTime = max_time

            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftKnee_x', 'rightKnee_x']]
            leftkneeMin = data['leftKnee_x'].min()
            rightkneeMax = data['rightKnee_x'].max()

            data['leftKneediff'] = (np.abs(data['leftKnee_x'].min() - data['leftKnee_x']) / 100) * 100
            data['rightKneediff'] = (np.abs(data['rightKnee_x'].max() - data['rightKnee_x']) / 100) * 100

            rightKneeError = np.average(data['rightKneediff'].nlargest(3))
            leftKneeError = np.average(data['leftKneediff'].nlargest(3, ))

            if rightKneeError >= 90 or leftKneeError >= 90:
                accuracy = 0.01
                accuracy_list.append(accuracy)
                accuracy_dict["step7"] = accuracy

        if 'step8' in step:
            minTime = min_time
            maxTime = max_time

            data = df[df['captureTime'].between(minTime, maxTime)]
            data = data[['captureTime', 'leftKnee_y', 'rightKnee_y', 'leftShoulder_y', 'rightShoulder_y']]
            data['left_knee_diff'] = data['leftKnee_y'] - data['leftShoulder_y']
            data['right_knee_diff'] = data['rightKnee_y'] - data['rightShoulder_y']
            # data = data[['left_knee_diff', 'right_knee_diff','leftKnee_y', 'rightKnee_y']]
            data['left_accuracy'] = data.apply(lambda x: Score.knee_bend_accuracy(x.left_knee_diff, x.leftKnee_y), axis=1)
            data['right_accuracy'] = data.apply(lambda x: Score.knee_bend_accuracy(x.right_knee_diff, x.rightKnee_y), axis=1)
            data = pd.concat([data['left_accuracy'], data['right_accuracy']], axis=0)
            try:
                accuracy = np.average(data.nlargest(5))
                accuracy_list.append(accuracy)
                accuracy_dict["step8"] = accuracy
            except:
                return 0

        print(dict(accuracy_dict))
        print("####################")

        if exercise_id == 3:
            # if accuracy_dict["step6"] != "empty" and accuracy_dict["step6"] == 0: '''user has not jumped then score
            # is 0  but that shouldn't be in accuracy list,bcz it will avg down the accuracy, but 0.01 means user has
            # done a random dance.''' accuracy_list.remove(0)

            if accuracy_dict["step6"] != "empty" and accuracy_dict["step6"] > 70:
                '''if user has jumped and distance in more than 80 (jump is too high than tolerance) then flag out, 
                also we are not using this value for avg, '''
                # print("@@@@@@ vertical jumpped")
                accuracy_score = 0
                return accuracy_score
            elif accuracy_dict["step6"] != "empty":
                accuracy_list.remove(accuracy_dict["step6"])

            if accuracy_dict["step7"] != "empty" and accuracy_dict["step7"] == 0.01:
                # but 0.01 means user did a random dance.
                # print("@@@@@ horizontal jumpped")
                accuracy_score = 0
                return accuracy_score

        elif exercise_id == 4:
            if accuracy_dict["step7"] != "empty" and accuracy_dict["step7"] < 10:
                accuracy_score = 0
                return accuracy_score

            if accuracy_dict["step8"] == "empty" or accuracy_dict["step8"] < 50:
                accuracy_score = 0
                return accuracy_score
            elif accuracy_dict["step8"] == "empty" or accuracy_dict["step8"] >= 80:
                # if user has bend as expected then don't add bend score. If not the add bend score to curb down result
                accuracy_list.remove(accuracy_dict["step8"])

        else:
            if "step6" in step or "step7" in step:
                if 0 in accuracy_list or 0.01 in accuracy_list:
                    # print("horizontal skipping trap")
                    accuracy_score = 0
                    return accuracy_score
        accuracy_score = np.round(np.average(accuracy_list))

        return accuracy_score

    @classmethod
    def _reformat_user_data(cls, user_df, instructor_df, exercise_id):
        instructor_df = instructor_df[instructor_df['exercise_id'] == exercise_id]
        user_df = user_df.merge(instructor_df, how='left', left_on="captureTime", right_on="capture_time")
        user_df.drop_duplicates(subset='captureTime', keep='first', inplace=True)
        user_df.index = np.arange(0, user_df.shape[0])
        return user_df

    @classmethod
    def _get_accuracy_score(cls, df, exercise_id):
        pose_score_list = []
        sample = 2
        instructor = pd.read_csv('resource/instructor_pose.csv')
        df = Score._reformat_user_data(df, instructor, exercise_id)
        for pose in df['pose'].unique():
            minTime, maxTime, step = Score._get_start_end(instructor, pose)
            pose_score_list.append(Score._get_score(minTime, maxTime, step, df, sample, exercise_id))
        score_series = pd.Series(pose_score_list).dropna()
        print(score_series)
        accuracy_score = np.ceil(np.average(score_series))
        print("######accuracy_score_actual", accuracy_score)
        if accuracy_score <= 0:
            accuracy_score = 0
        elif accuracy_score <= 32:
            accuracy_score = 0
        elif accuracy_score >= 100:
            accuracy_score = random.randint(90, 95)
            print("derived")
        return accuracy_score
