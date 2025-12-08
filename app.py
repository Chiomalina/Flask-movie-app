import requests
from requests.exceptions import RequestException

from flask import Flask, render_template, request, redirect, url_for, abort
from sqlalchemy.exc import SQLAlchemyError

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

def get_user_or_404(user_id: int):
	"""Fetch a user or abort with 404 if not found."""
	user = data_manager.get_user(user_id)
	if user is None:
		abort(404)
	return user


def get_movie_or_404(movie_id: int):
	"""Fetch a movie or abort with 404 if not found."""
	movie = data_manager.get_movie(movie_id)
	if movie is None:
		abort(404)
	return movie


@app.route("/")
def index():
	users = data_manager.get_all_users()
	#return render_template("index.html", users=users)
	return render_template("index.html")

@app.route("/users")
def list_users():
	try:
		users = data_manager.get_all_users()
	except SQLAlchemyError as e:
		app.logger.error(f"DB error while listing users: {e}")
		abort(500)
	return render_template("users.html", users=users)


@app.route("/users/<int:user_id>")
def user_movies(user_id):
	# Get the user (dict or model)
	user = get_user_or_404(user_id)

	# Get all movies from that user
	movies = data_manager.get_user_movies(user_id)

	return render_template("user_movies.html", user=user, movies=movies)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
	if request.method == "POST":
		name = request.form.get("name", "").strip()

		if not name:
			error = "Name is required."
			return render_template("add_user.html", error=error)

		try:
			# Use DataManager to create user
			data_manager.add_user(name=name)
		except SQLAlchemyError as e:
			app.logger.error(f"DB error while adding user '{name}': {e}")
			abort(500)

		return redirect(url_for("list_users"))

	# GET request -- just show the form
	return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
	# Ensure the user exists
	user = get_user_or_404(user_id)

	if request.method == "POST":
		title = request.form["title"]

		params = {
			"t": title,
			"apikey": OMDB_API_KEY,
		}

		try:
			response = requests.get("http://www.omdbapi.com/", params=params, timeout=5)
			# raises for 4xx/5xx HTTP status
			response.raise_for_status()
			data = response.json()
		except RequestException as e:
			app.logger.error(f"OMDb request failed: {e}")
			error = "Could not reach the movie service. Please try again later."
			return render_template("add_movie.html", user_id=user_id, error=error)
		except ValueError:
			# .json() failed
			app.logger.error("Invalid JSON received from OMDb")
			error = "Received invalid data from the movie service."
			return render_template("add_movie.html", user_id=user_id, error=error)

		# OMDb-specific logical error
		if data.get("Response") == "False":
			error = data.get("Error", "Movie not found")
			return render_template("add_movie.html", user_id=user_id, error=error)

		# Mapping
		movie_name = data.get("Title", title)
		raw_year = data.get("Year", "")
		movie_year = data_manager.parse_year(raw_year)

		imdb_rating_str = data.get("imdbRating")
		movie_rating = (
			float(imdb_rating_str)
			if imdb_rating_str and imdb_rating_str != "N/A"
			else 0.0
		)
		director = data.get("Director", "Unknown")

		# Save via DataManager
		try:
			data_manager.add_movie(
				user_id=user_id,
				name=movie_name,
				director=director,
				year=movie_year,
				rating=movie_rating,
			)
		except SQLAlchemyError as e:
			app.logger.error(f"DB error while adding movie for user {user_id}: {e}")
			abort(500)

		return redirect(url_for("user_movies", user_id=user_id))

	# GET -> show empty form
	return render_template("add_movie.html", user_id=user_id, user=user)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
	# Ensure the user exists

	user = get_user_or_404(user_id)

	if request.method == "POST":
		try:
			name = request.form["name"]
			director = request.form["director"]
			year = int(request.form["year"])
			rating = float(request.form["rating"])
		except (KeyError, ValueError):
			# Invalid form input -> re-render form with an error message
			movie = get_movie_or_404(movie_id)
			error = "Year must be a whole number and rating must be a number."
			return render_template(
				"update_movie.html",
				user_id=user_id,
				movie=movie,
				error=error,
			)

		try:
			data_manager.update_movie(
				movie_id=movie_id,
				name=name,
				director=director,
				year=year,
				rating=rating,
			)
		except SQLAlchemyError as e:
			app.logger.error(f"DB error while updating movie {movie_id}: {e}")
			abort(500)

		return redirect(url_for("user_movies", user_id=user_id))

	# Get - fetch movie and render the form with current values
	movie = data_manager.get_movie(movie_id)

	if movie is None:
		# Movie does not exist -> return 404 page
		abort(404)

	return render_template("update_movie.html", user_id=user_id, user=user, movie=movie)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["GET", "POST"])
def delete_movie(user_id, movie_id):
	get_user_or_404(user_id)
	get_movie_or_404(movie_id)

	try:
		data_manager.delete_movie(movie_id)
	except SQLAlchemyError as e:
		app.logger.error(f"DB error while deleting movie {movie_id}: {e}")
		abort(500)

	return redirect(url_for("user_movies", user_id=user_id))


@app.route("/users(<int:user_id>/movies/<int:movie_id>/add_review", method=["GET", "POST"])
def add_review(user_id, movie_id):
	# Ensure user and movie exist
	user = get_user_or_404(user_id)
	movie = get_movie_or_404(movie_id)

	if user is None or movie is None:
		abort(404)

	if request.method == "POST":
		review_text = request.form["review_text"]
		rating = float(request.form["rating"])

		data_manager.add_review(
			user_id=user_id,
			movie_id=movie_id,
			review_text=review_text,
			rating=rating,
		)

		# Back to the user's movie list
		return redirect(url_for("user_movies", user_id=user_id))

	# GET Requesst shows form
	return render_template(
		"add_review.html",
		user=user,
		movie=movie,
	)







@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
	return render_template("500.html"), 500


if __name__ == "__main__":
	app.run(debug=True)