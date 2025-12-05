import requests
from flask import Flask, render_template, request, redirect, url_for
from models import db
from datamanager.sqlite_data_manager import SQLiteDataManager
from dotenv import load_dotenv
import os

load_dotenv()

OMDB_API_KEY = os.getenv("OMDb_API_KEY")

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
	return render_template("user_movies.html", user=user, movies=movies)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
	if request.method == "POST":
		name = request.form["name"]
		# Use DataManager to create user
		data_manager.add_user(name=name)
		return redirect(url_for("list_users"))

	# GET request -- just show the form
	return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
	if request.method == "POST":
		title = request.form["title"]

		#1. CAll OMDb API
		params = {
			"t": title,
			"apikey": OMDB_API_KEY,
		}
		response = requests.get("http://www.omdbapi.com/", params=params)
		data = response.json()

		#2. Extract fields (handle not found case)
		if data.get("Response") == "False":
			error = data.get("Error", "Movie not found")
			# re-render template with error message
			return render_template(
				"add_movie.html",
				user_id=user_id,
				error=error,
			)

		# Mapping
		movie_name = data.get("Title", title)
		movie_year = int(data.get("Year", 0)) if data.get("Year") else 0
		# OMDb uses "imdbRating"
		imdb_rating_str = data.get("imdbRating")
		movie_rating = float(imdb_rating_str) if imdb_rating_str and imdb_rating_str != "N/A" else 0.0
		director = data.get("Director", "Unknown")

		#3. Save via DataManager
		data_manager.add_movie(
			user_id=user_id,
			name=movie_name,
			director=director,
			year=movie_year,
			rating=movie_rating,
		)

		return redirect(url_for("user_movies", user_id=user_id))

	# GET -> show empty form
	return render_template("add_movie.html", user_id=user_id)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
	if request.method == "POST":
		name = request.form["name"]
		director = request.form["director"]
		year = int(request.form["year"])
		rating = float(request.form["rating"])

		data_manager.update_movie(
			movie_id=movie_id,
			name=name,
			director=director,
			year=year,
			rating=rating,
		)
		return redirect(url_for("user_movies", user_id=user_id))

	# GET - fetch movie and render the form with current values
	movie = data_manager.get_movie(movie_id)
	return render_template("update_movie.html", user_id=user_id, movie=movie)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["GET", "POST"])
def delete_movie(user_id, movie_id):
	data_manager.delete_movie(movie_id)
	return redirect(url_for("user_movies", user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
	return render_template("500.html"), 500


if __name__ == "__main__":
	app.run(debug=True)