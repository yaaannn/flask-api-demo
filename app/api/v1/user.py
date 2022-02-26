import time
from flask import jsonify, Blueprint, request
from app.common.md5_operate import get_md5
from app.common.mysql_operate import db
from app.common.result_restful import error, success
from app.common.redis_operate import redis_db

main = Blueprint('user', __name__)


@main.route('/all', methods=['GET'])
def get_all_users():
    """获取所用用户"""
    sql = "select * from user"
    data = db.select_db(sql)
    return success(data, 0, '查询成功')


@main.route('/register', methods=['POST'])
def user_register():
    """注册用户"""
    username = request.json.get('username', '').strip()  # 获取用户名
    password = request.json.get("password", "").strip()  # 获取密码
    if username and password:  # 注意if条件中 "" 也是空, 按False处理
        sql1 = f"SELECT username FROM user WHERE username = '{username}'"
        res1 = db.select_db(sql1)
    if res1:
        return error(20001, "用户名已存在")
    else:
        password = get_md5(username, password)
        sql2 = f"INSERT INTO user (username, password) VALUES ('{username}', '{password}')"
        db.execute_db(sql2)
        return success(None, 0, "注册成功")


@main.route("/login", methods=['POST'])
def user_login():
    """登录用户"""
    username = request.values.get("username", "").strip()
    password = request.values.get("password", "").strip()
    if username and password:  # 注意if条件中空串 "" 也是空, 按False处理
        sql1 = f"SELECT username FROM user WHERE username = '{username}'"
        res1 = db.select_db(sql1)
        if not res1:
            return error(2001, "用户不存在")

        md5_password = get_md5(username, password)  # 把传入的明文密码通过MD5加密变为密文
        sql2 = f"SELECT * FROM user WHERE username = '{username}' and password = '{md5_password}'"
        res2 = db.select_db(sql2)
        if res2:
            timeStamp = int(time.time())  # 获取当前时间戳
            token = get_md5(username, str(timeStamp))  # MD5加密后得到token
            redis_db.handle_redis_token(username, token)  # 把token放到redis中存储
            login_info = {  # 构造一个字段，将 id/username/token/login_time 返回
                "id": res2[0]["id"],
                "username": username,
                "token": token,
                "login_time": time.strftime("%Y/%m/%d %H:%M:%S")
            }
            return success(login_info, 0, "登录成功")
        return error(1002, "用户名或密码错误")
    else:
        return error(1001, "用户名或密码不能为空")


@main.route("/update/<int:id>", methods=['PUT'])
def user_update(id):  # id为准备修改的用户ID
    """修改用户信息"""
    username = request.json.get("username", "").strip()
    token = request.json.get("token", "").strip()  # token口令
    new_password = request.json.get("password", "").strip()  # 新的密码
    if username and token and new_password:  # 注意if条件中空串 "" 也是空, 按False处理
        redis_token = redis_db.handle_redis_token(username)  # 从redis中取token
        if redis_token:
            if redis_token == token:  # 如果从redis中取到的token不为空，且等于请求body中的token
                sql1 = f"SELECT * FROM user WHERE id = '{id}'"
                res2 = db.select_db(sql1)
                if not res2:  # 如果要修改的用户不存在于数据库中，res2为空
                    return error(4005, "修改的用户ID不存在")
                else:
                    # 把传入的明文密码通过MD5加密变为密文
                    new_password = get_md5(res2[0]["username"], new_password)
                    sql2 = f"UPDATE user SET password = '{new_password}' WHERE id = {id}"
                    db.execute_db(sql2)
                    return success(0, "修改成功")
            else:
                return error(4003, "token错误")
        else:
            return error(4002, "token不存在")
    else:
        return error(4001, "用户名或密码不能为空")


@main.route("/delete/<int:id>", methods=['DELETE'])
def user_delete(id):  # id为准备删除的用户ID
    """删除用户"""
    username = request.json.get("username", "").strip()
    token = request.json.get("token", "").strip()  # token口令
    if username and token:  # 注意if条件中空串 "" 也是空, 按False处理
        redis_token = redis_db.handle_redis_token(username)  # 从redis中取token
        if redis_token:
            if redis_token == token:
                sql1 = f"SELECT * FROM user WHERE id = '{id}'"
                res2 = db.select_db(sql1)
                if not res2:
                    return error(4005, "删除的用户ID不存在")
                else:
                    sql2 = f"DELETE FROM user WHERE id = {id}"
                    db.execute_db(sql2)
                    return success(0, "删除成功")
            else:
                return error(4003, "token错误")
        else:
            return error(4002, "token不存在")
    else:
        return error(4001, "用户名或密码不能为空")
