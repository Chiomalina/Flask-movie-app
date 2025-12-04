from flask import Flask, render_template, request, redirect, url_for
from models import db
from datamanager.sqlite_data_manager import SQLiteDataManager


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///moviweb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
	db.create_all()


data_manager = SQLiteDataManager("moviweb.db")

@app.route("/")
def index():
	users = data_manager.get_all_users()
	#return render_template("index.html", users=users)
	return "Welcome to Linas Movie App"

@app.route("/users")
def list_users():
	users = data_manager.get_all_users()
	return render_template("users.html", users=users)


@app.route("/users/create", methods=["POST"])
def create_user():
	name = request.form["name"]
	data_manager.add_user(name=name)
	return redirect(url_for("list_users"))


@app.route("/users/<int:user_id>")
def user_movies(user_id):
	# Get the user (dict or model)
	user = data_manager.get_user(user_id)

	# Get all movies from that user
	movies = data_manager.get_user_movies(user_id)

	# TODO: Add/Edit/Delete link here
	return f"Movies for user {user_id}"


if __name__ == "__main__":
	app.run(debug=True)