from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.follow import FollowMemoResource, FollowResource
from resources.memo import MemoListResource, MemoResource
from resources.user import UserRegisterResource, UserLoginResource, UserLogoutResource
# 로그아웃 관련된 import문
from resources.user import jwt_blocklist

app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)
# JWT 매니저를 초기화
jwt = JWTManager(app)
# 로그아웃된 토큰으로 요청하면, 실행되지 않게 처리하는 코드
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

api.add_resource(UserRegisterResource, "/user/register")
api.add_resource(UserLoginResource, "/user/login")
api.add_resource(UserLogoutResource, "/user/logout")
api.add_resource(MemoResource, "/memo/<int:memo_id>")
api.add_resource(MemoListResource, "/memo")
api.add_resource(FollowResource, "/follow/<int:user_id>")
api.add_resource(FollowMemoResource, "/follow")

if __name__ == "__main__" : 
    app.run()
