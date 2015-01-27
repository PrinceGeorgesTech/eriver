from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route("/")
def index():
    return render_template('home.html')


@app.route("/events")
def events():
    return render_template('events.html')


@app.route("/info")
def info():
    return render_template('info.html')

@app.route("/libraries")
def libraries():
    return render_template('base.html',
        title = "Libraries in East Riverdale",
        header = "Libraries",
        content = "Visit a local library below!")

@app.route("/schools")
def schools():
    return render_template('base.html',
        title = "Public Schools in East Riverdale",
        header = "Public Schools",
        content = "Need info on a public school? See below!")

@app.route("/officials")
def officials():
    return render_template('base.html',
        title = "Elected Officials for the East Riverdale Community",
        header = "Elected Officials for East Riverdale",
        content = "Need to contact an elected official? See below!")

if __name__ == "__main__":
    app.run(debug=True)
