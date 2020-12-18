import flask

app = flask.Flask(__name__, )


@app.route('/')
def hello_world():
    return "21903871293", 600213


@app.route("/lol.txt")
def pog():
    return "log", 200

if __name__ == '__main__':
    app.run()
