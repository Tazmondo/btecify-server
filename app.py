from flask import Flask
from flask import request


app = Flask(__name__)
with open("secret", "rb") as f:
    SECRETKEY = f.read()


@app.route('/')
def hello_world():
    return "btecify on top!"


if __name__ == '__main__':
    app.run(debug=True, host="195.188.1.165")
