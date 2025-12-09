from flask import Blueprint, jsonify, request, abort
from datamanager.sqlite_data_manager import SQLiteDataManager

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
	director = data["director"]
	if not isinstance(director, str):
		return jsonify({"error": "director must be a string (name)"}), 400

	try:
		year = int(data["year"])
		rating = float(data["rating"])
	except (ValueError, TypeError):
		return (
			jsonify({"error": "Year must be an integer and rating must be a number"}), 400,
		)

	# 4. Create the movie via DataManager
	created_movie = data_manager.add_movie(
		user_id=user_id,
		name=name,
		director=director,
		year=year,
		rating=rating,
	)

	# 5. Convert SQLAlchemy returned model to dictionary
	movie_dict = (
		created_movie
		if isinstance(created_movie, dict)
		else movie_to_dict(created_movie)
	)

	return jsonify(movie_dict), 201

