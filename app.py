from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from passlib.hash import sha256_crypt as sha256
from flask_login import LoginManager, login_user, login_required, current_user
from db import userdb, Playlist, AccessRow, User

app = Flask(__name__)
api = Api(app)
loginmanager = LoginManager()
loginmanager.init_app(app)
with open("secret", "rb") as f:
    app.secret_key = f.read()


def validatejson(json: dict, validation: dict):
    '''Validate some json information given a validation table.

    :param json: Some JSON input. Must be a dict, otherwise ValueError is raised.
    :param validation: Dictionary, where key is the JSON field, and the value is the type.
    '''
    if type(json) is not dict or type(validation) is not dict:
        raise ValueError("Must be provided with a dict.")
    for key, item in validation.items():
        if key not in json:
            return False
        if type(json[key]) is not item:
            return False

    return True


@loginmanager.user_loader
def userloader(userid):
    return userdb.getrow(userid)


@api.resource('/authenticate')
class LoginResource(Resource):
    def post(self):
        requestjson = request.get_json()
        validfields = {
            'username': str,
            'password': str
        }
        if not validatejson(requestjson, validfields):
            return "Please provide valid JSON arguments. username and password.", 400

        if requestjson['username'] not in userdb:
            return "Invalid username.", 422

        user = userdb.getrow(requestjson['username'])
        if not user.validate(requestjson['password']):
            return f"Incorrect password: {requestjson['password']}", 401

        login_user(user, remember=True)

    def put(self):  # todo: test me
        requestjson = request.get_json()
        validfields = {
            'username': str,
            'password': str,
            'apikey': str
        }
        if not validatejson(requestjson, validfields):
            return "Invalid JSON arguments", 400

        username = requestjson['username']
        password = requestjson['password']
        apikey = requestjson['apikey']

        if userdb.getrow(username) is not None:
            return "Username already taken", 422

        newuser = User(username, sha256.hash(password), apikey)
        userdb.createrow(username, newuser)

        return "Successfully created user", 200


@api.resource('/playlist')
class PlaylistResource(Resource):
    decorators = [
        login_required
    ]

    def get(self):
        return jsonify(current_user.getjsonplaylists()), 200

    def post(self):
        """POST playlist data for a logged in user.

        JSON should consist of a list of playlists.

        Each playlist should have {playlistname: str, songs: list[Song]}. Playlistname is a string,
        songs is a list of songs.

        Each song must have {songname: str, songurl: str, duration: str, author: str}.
        """
        json = request.get_json()
        playlistlist = [Playlist.playlistfromjson(playlist) for playlist in json]
        with AccessRow(userdb, current_user.getname()) as data:
            data.setplaylists(playlistlist)

        return "Success", 200


@app.route('/')
def hello_world():
    r = make_response("btecify on top!😤😤😤😤😤")
    return r


@app.route('/testauth')
@login_required
def testauth():
    return "You are authorised!", 200


if __name__ == '__main__':
    app.run()
