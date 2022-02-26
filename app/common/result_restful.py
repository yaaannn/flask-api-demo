# restful_utils.py
from flask import jsonify

# class HttpCode(object):
#     ok = 200
#     un_auth_error = 401
#     params_error = 400
#     server_error = 500


def restful_result(data, code, message):
    return jsonify({
        "data": data or {},
        "mate": {
            "status": code,
            "message": message,
        }
    })


def success(data=None, code=None, message=""):
    """
    正确返回
    """
    return restful_result(data=data, code=code, message=message)


def error(code=None, message=""):
    """
    错误返回
    """
    return restful_result(data=None, code=code, message=message)
