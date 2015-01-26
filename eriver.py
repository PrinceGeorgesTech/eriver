from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route("/")
def index():
    return render_template('base.html')


@app.route("/events")
def events():
    return render_template('base.html')


@app.route("/info")
def info():
    return render_template('base.html')


if __name__ == "__main__":
    app.run(debug=True)
