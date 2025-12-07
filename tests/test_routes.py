# tests/test_routes.py
"""
Route and integration tests for the Movie Web App.

This file tests:
- Basic routes ("/", "/users")
- User details page ("/users/<user_id>")
- Adding users (GET and POST)
- Adding movies (GET and POST, with a mocked OMDb API call)
- Updating movies (GET and POST, including invalid input)
- Deleting movies
- Error handling (404)

All tests use pytest and Flask's test client.
"""

import pytest
from app import app
from models import db, User, Movie


# =====================================================================
# FIXTURES AND HELPERS
# =====================================================================

@pytest.fixture
def client():
    """
    This fixture creates a test client that we pass to tests as `client`.

    - app.config["TESTING"] = True puts Flask into testing mode.
    - app.test_client() returns a "fake browser" we can use to send
      GET and POST requests to our routes without running the server.

    Any test that includes `client` as a parameter will automatically
    receive this object.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        # provide the test client to the test function
        yield client


@pytest.fixture(autouse=True)
def clean_db():
    """
    This fixture runs automatically BEFORE each test (autouse=True).

    It clears the User and Movie tables, so every test starts with a
    clean database. This prevents data created in one test from affecting
    other tests.
    """
    with app.app_context():
        # Delete movies first because of the foreign key from Movie to User
        Movie.query.delete()
        User.query.delete()
        db.session.commit()

    # After the test runs, control returns here, then fixture ends
    yield


def create_user(name: str = "Test User") -> int:
    """
    Helper function to insert a user directly into the database and
    return the new user's ID.

    We use this to set up data for tests that need an existing user.
    """
    with app.app_context():
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user.id


def create_movie(
    user_id: int,
    name: str = "Test Movie",
    director: str = "Test Director",
    year: int = 2000,
    rating: float = 7.5,
) -> int:
    """
    Helper function to insert a movie for a given user and return the
    movie's ID.

    We use this when testing routes that require existing movies.
    """
    with app.app_context():
        movie = Movie(
            name=name,
            director=director,
            year=year,
            rating=rating,
            user_id=user_id,
        )
        db.session.add(movie)
        db.session.commit()
        return movie.id


# =====================================================================
# BASIC ROUTES
# =====================================================================

def test_index_route(client):
    """
    GET / should return status 200 and the welcome text.

    This tests the `index` route:
        @app.route("/")
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Linas Movie App" in response.data


def test_list_users_route_empty_db(client):
    """
    GET /users when the database has no users yet.

    The page should still load with status 200, even if the list is empty.
    """
    response = client.get("/users")
    assert response.status_code == 200

    # This assertion is intentionally very loose: it just checks that the
    # word "user" appears somewhere in the HTML (case-insensitive).
    assert b"user" in response.data.lower()


# =====================================================================
# /users/<user_id> (USER MOVIES PAGE)
# =====================================================================

def test_user_movies_existing_user_with_movies(client):
    """
    GET /users/<user_id> for a real user who has at least one movie.

    This should:
    - return status 200
    - show the user's name
    - show the movie name
    """
    user_id = create_user(name="Lina")
    movie_id = create_movie(user_id, name="Inception")

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert b"Lina" in response.data
    assert b"Inception" in response.data


def test_user_movies_nonexistent_user_returns_404(client):
    """
    GET /users/<user_id> for a user that does not exist.

    The helper `get_user_or_404` should call abort(404), so the route
    should return a 404 status code.
    """
    response = client.get("/users/99999")
    assert response.status_code == 404


# =====================================================================
# /add_user (ADD USER ROUTE)
# =====================================================================

def test_add_user_get_shows_form(client):
    """
    GET /add_user should show the "Add User" form with status 200.
    """
    response = client.get("/add_user")
    assert response.status_code == 200

    assert b"add user" in response.data.lower() or b"name" in response.data.lower()


def test_add_user_post_creates_user_and_redirects(client):
    """
    POST /add_user should:
    - create a new user in the database
    - redirect to the /users page.
    """
    response = client.post(
        "/add_user",
        data={"name": "Test User"},
        follow_redirects=False,  # we first want to check the redirect
    )

    # Expect a redirect status
    assert response.status_code == 302

    # The "Location" header tells us where we are redirected to
    location = response.headers.get("Location")
    assert location is not None
    assert "users" in location

    # Now, follow the redirect and see if the user appears on the page
    follow_response = client.get(location)
    assert follow_response.status_code == 200
    assert b"Test User" in follow_response.data

    # Finally, confirm the user exists in the database
    with app.app_context():
        user = User.query.filter_by(name="Test User").first()
        assert user is not None


def test_add_user_post_without_name_shows_error(client):
    """
    If we POST to /add_user without a name, the route should re-render
    the form with an error message instead of redirecting.
    """
    response = client.post("/add_user", data={"name": ""})
    assert response.status_code == 200
    assert b"Name is required" in response.data


# =====================================================================
# /users/<user_id>/add_movie (ADD MOVIE ROUTE)
# =====================================================================

def test_add_movie_get_shows_form(client):
    """
    GET /users/<user_id>/add_movie should show the "Add Movie" form if
    the user exists.
    """
    user_id = create_user()
    response = client.get(f"/users/{user_id}/add_movie")
    assert response.status_code == 200

    # Again, adjust based on your add_movie.html template content.
    assert b"add movie" in response.data.lower() or b"title" in response.data.lower()


def test_add_movie_get_for_nonexistent_user_404(client):
    """
    If the user does not exist, GET /users/<user_id>/add_movie should return 404.
    """
    response = client.get("/users/99999/add_movie")
    assert response.status_code == 404


def test_add_movie_post_success(client, monkeypatch):
    """
    POST /users/<user_id>/add_movie with a valid title should:

    - Call OMDb (we mock this part)
    - Create a movie in the database
    - Redirect to /users/<user_id>
    """

    # First, create a real user
    user_id = create_user()

    # ---- Mock requests.get used in app.add_movie ----

    class FakeResponse:
        """
        This fake response imitates the object returned by requests.get().
        We only implement the methods that the code under test uses.
        """

        def raise_for_status(self):
            # In a real request, this would raise an HTTPError for bad status codes.
            # Here we do nothing, pretending everything is fine.
            pass

        def json(self):
            # This is the fake JSON data we want OMDb to "return".
            return {
                "Response": "True",
                "Title": "Inception",
                "Year": "2010",
                "imdbRating": "8.8",
                "Director": "Christopher Nolan",
            }

    def fake_get(url, params=None, timeout=None):
        """
        Replacement for requests.get that always returns FakeResponse.
        """
        return FakeResponse()

    # IMPORTANT: Patch "app.requests.get" because we did "import requests" in app.py
    monkeypatch.setattr("app.requests.get", fake_get)

    # ---- Act: submit the form ----

    response = client.post(
        f"/users/{user_id}/add_movie",
        data={"title": "Inception"},
        follow_redirects=False,
    )

    # ---- Assert: redirect and DB changes ----

    assert response.status_code == 302
    location = response.headers.get("Location")
    assert location is not None
    assert f"/users/{user_id}" in location

    # Check database for the new movie
    with app.app_context():
        movie = Movie.query.filter_by(user_id=user_id, name="Inception").first()
        assert movie is not None
        assert movie.director == "Christopher Nolan"
        assert movie.year == 2010
        assert movie.rating == 8.8


def test_add_movie_post_omdb_not_found_shows_error(client, monkeypatch):
    """
    If OMDb returns Response=False, the route should re-render the form
    with the error returned by OMDb.
    """

    user_id = create_user()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "Response": "False",
                "Error": "Movie not found!",
            }

    def fake_get(url, params=None, timeout=None):
        return FakeResponse()

    monkeypatch.setattr("app.requests.get", fake_get)

    response = client.post(
        f"/users/{user_id}/add_movie",
        data={"title": "Unknown Movie"},
        follow_redirects=False,
    )

    # No redirect in this case, just re-rendered form
    assert response.status_code == 200
    assert b"Movie not found" in response.data


# =====================================================================
# /users/<user_id>/update_movie/<movie_id> (UPDATE MOVIE ROUTE)
# =====================================================================

def test_update_movie_get_existing_movie(client):
    """
    GET /users/<user_id>/update_movie/<movie_id> for an existing movie
    should load the form and show current values.
    """
    user_id = create_user("Lina")
    movie_id = create_movie(user_id, name="Old Title")

    response = client.get(f"/users/{user_id}/update_movie/{movie_id}")
    assert response.status_code == 200
    assert b"Old Title" in response.data


def test_update_movie_get_nonexistent_movie_404(client):
    """
    GET /users/<user_id>/update_movie/<movie_id> for a non-existing movie
    should return 404.
    """
    user_id = create_user()
    response = client.get(f"/users/{user_id}/update_movie/99999")
    assert response.status_code == 404


def test_update_movie_post_success(client):
    """
    POST /users/<user_id>/update_movie/<movie_id> with valid data should:
    - update the movie in the database
    - redirect to /users/<user_id>
    """
    user_id = create_user()
    movie_id = create_movie(user_id, name="Old Title", director="Old Director")

    response = client.post(
        f"/users/{user_id}/update_movie/{movie_id}",
        data={
            "name": "New Title",
            "director": "New Director",
            "year": "2020",
            "rating": "9.0",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    location = response.headers.get("Location")
    assert location is not None
    assert f"/users/{user_id}" in location

    # Confirm DB changes
    with app.app_context():
        movie = Movie.query.get(movie_id)
        assert movie is not None
        assert movie.name == "New Title"
        assert movie.director == "New Director"
        assert movie.year == 2020
        assert movie.rating == 9.0


def test_update_movie_post_invalid_data_shows_error(client):
    """
    If the POST data has invalid year or rating (cannot be converted),
    the route should re-render the form with an error message.
    """
    user_id = create_user()
    movie_id = create_movie(user_id)

    response = client.post(
        f"/users/{user_id}/update_movie/{movie_id}",
        data={
            "name": "Some Title",
            "director": "Some Director",
            "year": "not_a_year",
            "rating": "not_a_float",
        },
    )

    assert response.status_code == 200
    assert b"Year must be a whole number and rating must be a number." in response.data


# =====================================================================
# /users/<user_id>/delete_movie/<movie_id> (DELETE MOVIE ROUTE)
# =====================================================================

def test_delete_movie_success(client):
    """
    GET /users/<user_id>/delete_movie/<movie_id> for a real movie
    should delete the movie and redirect back to /users/<user_id>.
    """
    user_id = create_user()
    movie_id = create_movie(user_id)

    response = client.get(
        f"/users/{user_id}/delete_movie/{movie_id}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    location = response.headers.get("Location")
    assert location is not None
    assert f"/users/{user_id}" in location

    # Confirm the movie is removed from DB
    with app.app_context():
        movie = Movie.query.get(movie_id)
        assert movie is None


def test_delete_movie_nonexistent_user_404(client):
    """
    If the user does not exist when deleting a movie, we should get 404.
    """
    response = client.get("/users/99999/delete_movie/1")
    assert response.status_code == 404


def test_delete_movie_nonexistent_movie_404(client):
    """
    If the movie does not exist for an existing user, we should get 404.
    """
    user_id = create_user()
    response = client.get(f"/users/{user_id}/delete_movie/99999")
    assert response.status_code == 404


# =====================================================================
# ERROR HANDLING (404)
# =====================================================================

def test_404_handler_works_for_unknown_route(client):
    """
    Any completely unknown route should hit the 404 error handler and
    return status 404 with a helpful message.
    """
    response = client.get("/this-route-does-not-exist-at-all")
    assert response.status_code == 404

    assert b"404" in response.data or b"not found" in response.data.lower()
