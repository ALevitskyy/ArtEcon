from flask import Flask, Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from flask_script import Manager
from flask_basicauth import BasicAuth
from flask.ext.session import Session
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from models import Post, Tag, Comment, db


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(
            message,
            Response(
                "You could not be authenticated. Please refresh the page.",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            ),
        )


def inaccessible_callback(self, name, **kwargs):
    return redirect(basic_auth.challenge())


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_COMMIT_OR_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["BASIC_AUTH_USERNAME"] = os.environ["SECRET_KEY"]
app.config["BASIC_AUTH_PASSWORD"] = os.environ["SECRET_KEY"]
Session(app)
basic_auth = BasicAuth(app)


class ModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException("Not authenticated.")
        else:
            return True


admin = Admin(app)
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Comment, db.session))

db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
# if __name__ == "__main__":
#    manager.run()
