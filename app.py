from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from passlib.hash import sha256_crypt
from flask_login import LoginManager, login_user, login_required, current_user
import flask
import db
from db import userdb, Playlist, AccessRow

app = Flask(__name__)
api = Api(app)
loginmanager = LoginManager()
loginmanager.init_app(app)
with open("secret", "rb") as f:
    app.secret_key = f.read()


@loginmanager.user_loader
def userloader(userid):
    return userdb.getrow(userid)


@api.resource('/authenticate')
class LoginResource(Resource):
    def post(self):
        y = request.get_json()
        if y is None or 'username' not in y or 'password' not in y:
            return "Please provide valid JSON arguments. username and password.", 400

        if y['username'] not in userdb:
            return "Invalid username.", 400

        user = userdb.getrow(y['username'])
        if not user.validate(y['password']):
            return f"Incorrect password: {y['password']}", 401

        login_user(user, remember=True)

        pass  # TODO: Add functionality and other functions as well


@api.resource('/playlist')
class PlaylistResource(Resource):
    decorators = [
        login_required
    ]

    def get(self):
        return jsonify(current_user.getjsonplaylists())

    def post(self):
        json = request.get_json()
        playlistlist = [Playlist.playlistfromjson(playlist) for playlist in json]
        with AccessRow(userdb, current_user.name()) as data:
            data.setplaylists(playlistlist)


@app.route('/')
def hello_world():
    r = make_response("btecify on top")
    return r


@app.route('/testauth')
def testauth():
    return "You are authorised!", 200


if __name__ == '__main__':
    app.run()
