from flask import Flask, render_template 
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('base.html', 
    	title = "Home", 
    	header = "Information", 
    	content = "Content is here")

if __name__ == "__main__":
    app.run()