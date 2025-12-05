from abc import ABC, abstractmethod
from  typing import List, Dict, Any, Optional

class DataManagerInterface(ABC):
	"""Abstract interface for data management of users and their movies"""

	# ----- User operations -----
	@abstractmethod
	def get_all_users(self) -> List[Any]:
		"""Return a list of all users."""
		pass

	@abstractmethod
	def get_user(self, user_id: int) -> Optional[Any]:
		"""Return a single user by ID."""
		pass

	@abstractmethod
	def add_user(self, name: str) -> Any:
		"""Return a list of all users."""
		pass

	# ----- Movies -----
	@abstractmethod
	def get_user_movies(self, user_id: int) -> List[Any]:
		"""Return all movies that belong to the given user."""
		pass

	@abstractmethod
	def add_movie(
			self,
			user_id: int,
			name: str,
			director: str,
			year: int,
			rating: float,
	) -> Any:
		"""Create a new movie for a given user and return it."""
		pass

	@abstractmethod
	def update_movie(
			self,
			movie_id: int,
			**fields: Any,
	) -> Optional[Any]:
		"""Update fields of an existing movie. Return updated movie or None."""
		pass

	@abstractmethod
	def delete_movie(self, movie_id: int) -> bool:
		"""Delete a movie by id. Return True if deleted, False if not found."""
		pass

