from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)

	movies = db.relationship(
		"Movie",
		back_populates="user",
		cascade="all, delete-orphan",
	)

class Movie(db.Model):
	__tablename__ = "movies"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	director = db.Column(db.String, nullable=False)
	year = db.Column(db.Integer, nullable=False)
	rating = db.Column(db.Float, nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	user = db.relationship("User", back_populates="movies")
