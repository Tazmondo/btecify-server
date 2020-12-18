from flask import Flask
from flask import request
import flask
import db

app = Flask(__name__)
SECRETKEY = None
try:
    with open("secret", "rb") as f:
        SECRETKEY = f.read()
except FileNotFoundError:
    raise FileNotFoundError  # TODO: Do something else maybe later idk


@app.route('/')
def hello_world():
    x = request
    return "21903871293", 600213


if __name__ == '__main__':
    app.run()
