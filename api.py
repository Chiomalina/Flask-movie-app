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
		"director": movie.director,
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
