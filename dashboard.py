from flask import Flask, render_template, jsonify
from db.database import Database

bids = Database("db/bids")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bids")
def get_bids():
    bids.read_data()
    return jsonify(bids.data)

if __name__ == "__main__":
    app.run()