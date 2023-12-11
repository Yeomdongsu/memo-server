from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mysql.connector import Error
from mysql_connection import get_connection

class FollowResource(Resource) :
    # 친구 맺기
    @jwt_required()
    def post(self, followee_id) :

        user_id = get_jwt_identity()
        
        if followee_id == user_id :
            return {"error" : "자기 자신과는 친구할 수 없습니다."}, 400
        
        try :
            connection = get_connection()

            query = '''
                    insert into follow
                    (followerId, followeeId)
                    values
                    (%s, %s);
                    '''
            record = (user_id, followee_id)
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
    def delete(self, followee_id) :
        
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query ='''
                    delete from follow
                    where followerId = %s and followeeId = %s;
                    '''
            record = (user_id, followee_id)
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

class FollowMemoResourece(Resource) :
     # 내 친구 메모만 불러오기
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        offset = request.args.get("offset")
        limit = request.args.get("limit")

        try :
            connection = get_connection()

            query = '''
                    select s.id, u.id, u.nickname, s.title, s.date, s.content, s.createdAt, s.updatedAt
                    from summary s
                    join follow f
                    on s.userId = f.followeeId
                    join user u
                    on s.userId = u.id
                    where f.followerId = %s and now() < s.date
                    order by s.date asc
                    limit ''' + offset + ''', ''' + limit + ''';
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
