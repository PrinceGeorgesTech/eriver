from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route("/")
def index():
    return render_template(
        'base.html',
        title="Home",
        header="Information",
        content="Content is here")

if __name__ == "__main__":
    app.run()
