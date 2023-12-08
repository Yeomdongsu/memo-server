from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class MemoResource(Resource) :
    # 메모 생성
    @jwt_required()
    def post(self) :
        
        user_id = get_jwt_identity()
        
        data = request.get_json()

        try :
            connection = get_connection()

            query = '''
                    insert into summary
                    (title, date, content, userId)
                    values
                    (%s, %s, %s, %s);
                    '''
            record = (data["title"], data["date"], data["content"], user_id)

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
    
    # 메모 수정
    @jwt_required()
    def put(self, memo_id) :
        
        user_id = get_jwt_identity()

        data = request.get_json()

        try :
            connection = get_connection()

            query = '''
                    update summary
                    set title = %s, date = %s, content = %s
                    where id = %s and userId = %s;
                    '''
            record = (data["title"], data["date"], data["content"], memo_id, user_id)

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
    
    # 메모 삭제
    @jwt_required()
    def delete(self, memo_id) :

        user_id = get_jwt_identity()
        
        try :
            connection = get_connection()

            query = '''
                    delete from summary
                    where id = %s and userId = %s;
                    '''
            record = (memo_id, user_id)

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
    
class MemoListResource(Resource) :
    # 모든 메모 조회
    def get(self) :

        try : 
            connection = get_connection()

            query = '''
                    select * 
                    from summary;
                    '''
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
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
            return {"error" : "메모가 존재하지 않습니다."}, 400

        return {"result" : "success", "items" : memo_list, "count" : len(memo_list)}, 200