from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/documents")
def documents():
    return render_template("documents.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/help")
def help_page():
    return render_template("help.html")

if __name__ == "__main__":
    app.run(debug=True)
