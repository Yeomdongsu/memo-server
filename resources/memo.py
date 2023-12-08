from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class MemoListResource(Resource) :
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
    
    # 내 메모리스트 조회
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        # 쿼리스트링(쿼리 파라미터)에 있는 데이터를 받아온다.
        offset = request.args.get("offset")
        limit = request.args.get("limit")

        try : 
            connection = get_connection()

            query = '''
                    select id, title, date, content 
                    from summary
                    where userId = %s
                    order by date asc
                    limit ''' + str(offset) + ''', ''' + str(limit) + ''';
                    '''
            record = (user_id, )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            memo_list = cursor.fetchall()

            i = 0
            for row in memo_list :
                memo_list[i]["date"] = row["date"].isoformat()
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

class MemoResource(Resource) :
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