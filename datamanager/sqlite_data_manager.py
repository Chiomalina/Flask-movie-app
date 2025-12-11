from typing import List, Optional, Any, Dict
import re

from datamanager.data_manager_interface import DataManagerInterface
from models import db, User, Movie, Review, Director, Genre


class SQLiteDataManager(DataManagerInterface):
    """
    Concrete DataManager that uses SQLAlchemy ORM with a SQLite database.
    Assumes 'db' has already been initialized with a Flask app.
    """

    def __init__(self, db_file_name: str) -> None:
        # db_file_name is stored for reference; db/session is configured by Flask.
        self.db_file_name = db_file_name
        self.session = db.session

    # ---------- Helper ----------
    def parse_year(self, raw_year: str) -> int:
        """
        Extracts the first 4-digit year from a string like '2013–2015' or '2013– '.
        Returns 0 if no valid year is found.
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
        return user

    # ---------- Movie methods ----------
    def get_user_movies(self, user_id: int) -> List[Movie]:
        """Return all movies that belong to the given user."""
        return (
            self.session.query(Movie)
            .filter(Movie.user_id == user_id)
            .all()
        )

    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Return a single movie by ID, or None if not found."""
        return self.session.get(Movie, movie_id)

    def _get_or_create_director(self, director_name: str) -> Optional[Director]:
        """Helper: resolve a director name to a Director model (create if needed)."""
        director_name = (director_name or "").strip()
        if not director_name:
            return None

        director = (
            self.session.query(Director)
            .filter(Director.name == director_name)
            .first()
        )
        if director is None:
            director = Director(name=director_name)
            self.session.add(director)
            # flush so director.id is available before commit
            self.session.flush()
        return director

    def add_movie(
        self,
        user_id: int,
        name: str,
        director: str,
        year: int,
        rating: float,
        poster_url: str | None = None,
        genre: str | None = None,
    ) -> Movie:
        """
        Create a new movie for a user.

        :param user_id: ID of the user who owns the movie
        :param name: Movie title
        :param director: Director name (string)
        :param year: Release year
        :param rating: Rating as float
        :param genre: Optional genre name
        :return: The created Movie SQLAlchemy object
        """
        # 1. Ensure user exists (optional but defensive)
        user = User.query.get(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} does not exist")

        # 2. Find or create Director by name
        director_obj = Director.query.filter_by(name=director).first()
        if director_obj is None:
            director_obj = Director(name=director)
            db.session.add(director_obj)
            db.session.flush()  # so director_obj.id is available

        # 3. Find or create Genre by name (if provided)
        genre_obj = None
        if genre:
            genre_obj = Genre.query.filter_by(name=genre).first()
            if genre_obj is None:
                genre_obj = Genre(name=genre)
                db.session.add(genre_obj)
                db.session.flush()

        # 4. Create Movie using relationships `director` and `genre`
        movie = Movie(
            name=name,
            year=year,
            rating=rating,
            user_id=user_id,
            director=director_obj,
            genre=genre_obj,
            poster_url=poster_url,
        )

        db.session.add(movie)
        db.session.commit()

        return movie

    def update_movie(
        self,
        movie_id: int,
        **fields: Any,
    ) -> Optional[Movie]:
        """
        Update an existing movie with the given fields.

        Example:
            update_movie(1, name="New title", rating=9.0, director="Nolan")
        """
        movie = self.session.get(Movie, movie_id)
        if movie is None:
            return None

        # Handle director name specially
        if "director" in fields:
            director_name = fields.pop("director")
            director_obj = self._get_or_create_director(director_name)
            movie.director_obj = director_obj

        # Update any other simple attributes (name, year, rating, etc.)
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
        movie = self.session.get(Movie, movie_id)
        if movie is None:
            return False

        self.session.delete(movie)
        self.session.commit()
        return True

    # ---------- Review helpers ----------
    def _review_to_dict(self, review: Review) -> Dict[str, Any]:
        return {
            "id": review.id,
            "user_id": review.user_id,
            "movie_id": review.movie_id,
            "review_text": review.review_text,
            "rating": review.rating,
            "created_at": review.created_at,
        }

    # ---------- Review methods ----------
    def add_review(
        self,
        user_id: int,
        movie_id: int,
        review_text: str,
        rating: float,
    ) -> Dict[str, Any]:
        """Create and save a new review."""
        review = Review(
            user_id=user_id,
            movie_id=movie_id,
            review_text=review_text,
            rating=rating,
        )
        self.session.add(review)
        self.session.commit()
        return self._review_to_dict(review)

    def get_reviews_for_movie(self, movie_id: int) -> List[Dict[str, Any]]:
        """Return all reviews for a given movie as dicts."""
        reviews = (
            self.session.query(Review)
            .filter(Review.movie_id == movie_id)
            .all()
        )
        return [self._review_to_dict(r) for r in reviews]

    def get_reviews_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Return all reviews written by a given user as dicts."""
        reviews = (
            self.session.query(Review)
            .filter(Review.user_id == user_id)
            .all()
        )
        return [self._review_to_dict(r) for r in reviews]

    def delete_review(self, review_id: int) -> bool:
        """Delete a review by id. Return True if deleted, False if not found."""
        review = self.session.get(Review, review_id)
        if review is None:
            return False

        self.session.delete(review)
        self.session.commit()
        return True
