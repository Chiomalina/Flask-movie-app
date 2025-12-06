import pytest
from app import app
from models import db, User


@pytest.fixture
def client():
	"""
	Create a test client for the Flask app.
	TESTING=True tells Flask we are in test mode.
	"""
	app.config["TESTING"] = True

	with app.test_client() as client:
		yield client


def test_home_route(client):
	response = client.get("/users")

	assert response.status_code == 200
	assert b"user" in response.data


def test_add_user_get_shows_form(client):
	"""
	GET /add_user should return the form page with status 200.
	"""
	response = client.get("/add_user")
	# Status should be OK
	assert response.status_code == 200

	# Check that the page contains something that proves it's the add_user form
	assert b"Add User" in response.data or b"name" in response.data


def test_add_user_post_creates_user_and_redirects(client):
	"""
	POST /add_user with a name should:
	- create a user
	- redirect to the users list page
	"""

	with app.app_context():
		# Clear users if you want a clean slate for the test
		User.query.delete()
		db.session.commit()

	# Act: send POST data to the route
	response = client.post(
		"/add_user",
		data={"name": "Test User"},
		# we want to inspect the redirect itself first
		follow_redirects=False,
	)

	# Assert: we got a redirect (302)
	assert response.status_code == 302

	# Assert: the Location header points to something with "users" in it
	location = response.headers.get("Location")
	assert location is not None
	assert "users" in location

	# Now, optionally, follow the redirect and check the user list page
	follow_response = client.get(location)

	assert follow_response.status_code == 200
	assert b"Test User" in follow_response.data

	# And additionally, check DB content
	with app.app_context():
		user = User.query.filter_by(name="Test User").first()
		assert user is not None
