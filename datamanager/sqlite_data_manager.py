from typing import List, Optional, Any
import re

from datamanager.data_manager_interface import DataManagerInterface
from models import db, User, Movie

class SQLiteDataManager(DataManagerInterface):
	"""
	Concrete DataManager that uses SQLAlchemy ORM with a SQLite database.
	Assumes 'db' has already been initialized with a Flask app.
	"""

	def __init__(self, db_file_name: str) -> None:
		# Here we use db.session directly; no need to pass db_file_name here,
		# because the Flask app config already knows the DB URI.
		self.db_file_name = db_file_name
		self.session = db.session

	def parse_year(self, raw_year: str) -> int:
		"""
		Extracts the first 4-digit year from a string like '2013–2015' or '2013– '.
        Returns 0 if no valid year is found.
		:param raw_year:
		:return: int
		"""
		if not raw_year:
			return 0

		match = re.search(r"\d{4}", raw_year)
		if not match:
			return 0

		return int(match.group(0))

	# ---------- User methods ----------
	def get_all_users(self) -> List[User]:
		"""Return all users stored in the database."""
		return self.session.query(User).all()

	def get_user(self, user_id: int) -> Optional[User]:
		"""Return a single user by ID, or None if not found."""
		return self.session.get(User, user_id)

	def add_user(self, name: str) -> User:
		"""Create and persist a new user."""
		user = User(name=name)
		self.session.add(user)
		self.session.commit()
		# After commit, user.id is populated
		return user


	# ---------- Movie methods ----------
	def get_user_movies(self, user_id: int) -> List[Movie]:
		""" Return all movies that belong to the given user."""
		return (
			self.session.query(Movie)
			.filter(Movie.user_id == user_id)
			.all()
		)

	def get_movie(self, movie_id: int) -> Optional[Movie]:
		"""
		Fetch a single movie by its ID and return it as a dictionary.
		:param movie_id: ID of the movie to retrieve
		:return: dict with movie data or None if not found
		"""
		"""Return a single movie by ID, or None if not found."""
		return self.session.get(Movie, movie_id)



	def add_movie(
			self,
			user_id: int,
			name: str,
			director: str,
			year: int,
			rating: float,
	) -> Movie:
		""" Create and persist a new movie for the given user."""
		movie = Movie(
			user_id=user_id,
			name=name,
			director=director,
			year=year,
			rating=rating,
		)
		self.session.add(movie)
		self.session.commit()
		return movie

	def update_movie(
			self,
			movie_id: int,
			**fields: Any,
	) -> Optional[Movie]:
		"""
		    Update an existing movie with the given fields.

		    Example:
		    update_movie(1, name="New title", rating=9.0)
		"""
		movie = self.session.query(Movie).get(movie_id)
		if movie is None:
			return None

		# Only update attributes that exist on the model
		for key, value in fields.items():
			if hasattr(movie, key):
				setattr(movie, key, value)

		self.session.commit()
		return movie

	def delete_movie(self, movie_id: int) -> bool:
		"""
		Delete the movie with the given id.
		Return True if a movie was deleted, False otherwise.
		"""
		movie = self.session.query(Movie).get(movie_id)
		if movie is None:
			return False

		self.session.delete(movie)
		self.session.commit()
		return True

