from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from flask_restful import Resource
from mysql.connector import Error
from mysql_connection import get_connection
from utils import hash_password, check_password
from email_validator import validate_email, EmailNotValidError


class FollowResource(Resource) :
    # 친구 맺기
    @jwt_required()
    def post(self, user_id) :
        
        my_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''
                    insert into follow
                    (follower_id, followee_id)
                    values
                    (%s, %s);
                    '''
            record = (my_id, user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200
    
    # 친구 끊기
    @jwt_required()
    def delete(self, user_id) :
        
        my_id = get_jwt_identity()

        try :
            connection = get_connection()

            query ='''
                    delete from follow
                    where follower_id = %s and followee_id = %s;
                    '''
            record = (my_id, user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500
        
        return {"result" : "success"}, 200
    
class FollowMemoResource(Resource) :
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''
                    select * 
                    from summary s
                    join follow f
                    on s.userId = f.followee_id
                    where f.follower_id = %s;
                    '''
            record = (user_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            memo_list = cursor.fetchall()
            
            i = 0
            for row in memo_list :
                memo_list[i]["date"] = row["date"].isoformat()
                memo_list[i]["createdAt"] = row["createdAt"].isoformat()
                memo_list[i]["updatedAt"] = row["updatedAt"].isoformat()
                i = i+1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        if len(memo_list) == 0 :
            return {"error" : "친구가 없습니다."}, 400

        return {"result" : "success", "items" : memo_list, "count" : len(memo_list)}, 200

