from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # One user → many movies
    movies = db.relationship(
        "Movie",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # One user → many reviews
    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Director(db.Model):
    __tablename__ = "directors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)

    movies = db.relationship(
        "Movie",
        back_populates="director",
        cascade="all, delete-orphan",
    )


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

    movies = db.relationship(
        "Movie",
        back_populates="genre",
        cascade="all, delete-orphan",
    )


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    # Director / Genre FKs
    director_id = db.Column(db.Integer, db.ForeignKey("directors.id"), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=True)

    director = db.relationship("Director", back_populates="movies")
    genre = db.relationship("Genre", back_populates="movies")

    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    # Foreign key to users.id
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Many movies → one user
    user = db.relationship("User", back_populates="movies")

    # One movie → many reviews
    reviews = db.relationship(
        "Review",
        back_populates="movie",
        cascade="all, delete-orphan",
    )


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    review_text = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Many reviews → one user
    user = db.relationship("User", back_populates="reviews")

    # Many reviews → one movie
    movie = db.relationship("Movie", back_populates="reviews")
