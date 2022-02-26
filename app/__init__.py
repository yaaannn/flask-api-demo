from flask import Flask
from app.api.v1.user import main
from app.common.result_restful import error

from flasgger import Swagger, swag_from

app = Flask(__name__)

swagger = Swagger(app)


def create_app():

    app.register_blueprint(main, url_prefix="/api/user")
    # err
    return app


class Error:

    @app.errorhandler(404)
    def error_404(e):
        return error(404, "API Not Found")
