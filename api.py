from flask import Blueprint, jsonify, request, abort
from datamanager.sqlite_data_manager import SQLiteDataManager
from models import db, User, Movie, Director, Genre

data_manager = SQLiteDataManager("moviweb.db")

api = Blueprint("api", __name__)


def user_to_dict(user) -> dict:
	"""Convert a User SQLAlchemy model to a plain dict."""
	return {
		"id": user.id,
		"name": user.name,
		# More fields will be added later
	}


def movie_to_dict(movie) -> dict:
	"""Convert a Movie SQLAlchemy model to a plain dict."""
	return {
		"id": movie.id,
		"name": movie.name,
		"director_id": movie.director_id,
		"director_name": movie.director.name if movie.director else None,
		"genre_id": movie.genre_id,
		"genre_name": movie.genre.name if movie.genre else None,
		"year": movie.year,
		"rating": movie.rating,
		"user_id": movie.user_id,
	}


@api.route("/users", methods=["GET"])
def api_get_users():
	users = data_manager.get_all_users()
	user_data = [user_to_dict(user) for user in users]

	return jsonify(user_data), 200


@api.route("/users/<int:user_id>/movies", methods=["GET"])
def api_get_user_movies(user_id: int):
	"""Return all movies for a given user as JSON."""
	# 1. Check that the user exists
	user = data_manager.get_user(user_id)
	if user is None:
		abort(404, description=f"User with id {user_id} not found")

	# 2. Get the movies for the user
	movies = data_manager.get_user_movies(user_id)

	# 3. Convert to plain dicts
	movie_data = [movie_to_dict(movie) for movie in movies]

	return jsonify(movie_data), 200


@api.route("/users/<int:user_id>/movies", methods=["POST"])
def api_add_movie(user_id: int):
	"""
	Add a new favourite movie for a user.
	Expected JSON body:
	{
		"name": "Inception",
		"director": "Christopher Nolan",
		"genre": "Sci-Fi",
		"year": 2010,
		"rating": 9.0
	}
	"""
	# 1. Ensure the user exists
	user = data_manager.get_user(user_id)
	if user is None:
		abort(404, description=f"User with id {user_id} not found")

	# 2. Read JSON body
	data = request.get_json() or {}

	required_fields = ["name", "director", "year", "rating"]
	missing = [field for field in required_fields if field not in data]

	if missing:
		return (
			jsonify(
				{
					"error": "Missing required fields",
					"missing": missing,
				}
			),
			400,
		)

	# 3. Extract and lightly validate values
	name = data["name"]
	director_name = data["director"]
	genre_name = data.get("genre")

	if not isinstance(director_name, str):
		return jsonify({"error": "director must be a string (name)"}), 400

	try:
		year = int(data["year"])
		rating = float(data["rating"])
	except (ValueError, TypeError):
		return (
			jsonify({"error": "Year must be an integer and rating must be a number"}),
			400,
		)

	# 4. Find or create Director
	director = Director.query.filter_by(name=director_name).first()
	if director is None:
		director = Director(name=director_name)
		db.session.add(director)
		db.session.flush()  # so director.id is available

	# 5. (Optional) Find or create Genre
	genre = None
	if genre_name:
		genre = Genre.query.filter_by(name=genre_name).first()
		if genre is None:
			genre = Genre(name=genre_name)
			db.session.add(genre)
			db.session.flush()

	# 6. Create the Movie object
	movie = Movie(
		name=name,
		year=year,
		rating=rating,
		user_id=user_id,
		director=director,
		genre=genre,
	)

	db.session.add(movie)
	db.session.commit()

	# 7. Convert SQLAlchemy model to dict
	movie_dict = movie_to_dict(movie)

	return jsonify(movie_dict), 201