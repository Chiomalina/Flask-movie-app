🎬 MovieWeb — AI-Powered Flask Movie Collection App

A **production-ready Flask web application** that allows users to manage personal movie collections, enriched with **AI-generated trivia and reviews**, external movie data via **OMDb**, and a clean, modern UI.  
Built with strong software engineering principles: **OOP**, **database abstraction**, **RESTful design**, and **deployment-ready architecture**.

🚀 **Live Demo:**  
👉 https://chiomalina.pythonanywhere.com

---

## 📌 Project Overview

**MovieWeb** is a full-stack Python web application that enables users to:

- Create and manage users
- Add, update, and delete movies
- Fetch real movie data from the **OMDb API**
- Generate **AI-powered movie trivia and reviews**
- Persist data using **SQLite + SQLAlchemy ORM**
- Follow clean architecture using a **DataManager abstraction**
- Run in production on **PythonAnywhere**

This project was built with **maintainability, extensibility, and real-world deployment** in mind.

---

## 🧠 Key Features

### 👤 User Management
- Create users
- View user-specific movie collections
- Cascade delete (users → movies → reviews)

### 🎞️ Movie Management (CRUD)
- Add movies manually or via OMDb
- Update movie details
- Delete movies safely
- Ratings, years, directors, posters supported

### 🗄️ Database & ORM
- SQLite database
- SQLAlchemy ORM
- Proper relationships & foreign keys
- Cascading deletes for data integrity

### 🤖 AI Integrations
- AI-generated movie trivia
- AI-generated short reviews
- AI-generated movie recommendations
- Graceful fallback when AI services are unavailable

### 🌐 External API Integration
- **OMDb API** for:
  - Movie metadata
  - Posters
  - Release year, director, plot

### 🎨 Frontend & UX
- Jinja2 templating
- Reusable components
- Modern dark UI
- Responsive layout
- Clean typography and spacing

### 🚀 Deployment
- Production-ready Flask configuration
- Environment variables for secrets
- Deployed on **PythonAnywhere**
- Secure API key handling with `.env`

---

## 🧱 Tech Stack

### Backend
- **Python 3**
- **Flask**
- **Flask-SQLAlchemy**
- **Jinja2**
- **dotenv**

### Database
- **SQLite**
- **SQLAlchemy ORM**

### APIs & AI
- **OMDb API**
- **OpenAI API** (AI trivia & reviews)

### Frontend
- HTML5
- CSS3 (custom dark theme)
- Bootstrap utilities

### Deployment
- **PythonAnywhere**
- WSGI configuration
- Environment-based secrets

---

## 🗂️ Project Structure

```text
Flask_Movie_App/
│
├── app.py                  # Main Flask app & routes
├── api.py                  # API endpoints (AI, OMDb, JSON responses)
├── models.py               # SQLAlchemy models (User, Movie, Reviews, etc.)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (ignored by Git)
├── .gitignore
├── .README.md
│
├── datamanager/
│   ├── __init__.py
    ├── data_manager_interface.py
│   └── sqlite_data_manager.py
│
├── services/
│   ├── omdb_service.py     # OMDb API logic
│   └── ai_service.py       # OpenAI integration
│
├── templates/
│   ├── 404.html
│   ├── 500.html
│   ├── add_movie.html
│   ├── add_review.html
│   ├── add_user.html
    ├── ai_recommendations.html
    ├── ai_review.html
│   ├── ai_trivia.html
│   ├── base.html
│   ├── index.html
│   ├── movie_reviews.html
    ├── update_movie.html
    ├── user_movies.html
│   ├── users.html
│
├── static/
│   ├── css/
│   │   └── style.css
        └── error.css
│   └── images/
│
├── tests/
│   └── test_routes.py
│
└── instance/
    └── movieweb.db         # SQLite database
```

---
### Screenshots
- **User Dashboard**
- Movie Collection
- Movie Details & AI Trivia

---

### Demo Video
- **Full Walkthrough & Feature Demo**


---

### 🚀 Deployment Notes
- **Hosted on PythonAnywhere**
- WSGI configured for Flask
- Secure .env usage
- Production-ready settings

---

### 💡 What This Project Demonstrates
- **✔️ Real-world Flask architecture**
- ✔️ Database modeling & ORM mastery
- ✔️ API integration (external + AI)
- ✔️ Clean, readable, maintainable code
- ✔️ Full CRUD lifecycle
- ✔️ Deployment & production thinking

---

### 👤 Author
Lina Chioma Anaso
Software Engineering Student | Full-Stack Developer

🔗 GitHub: (add link)
🔗 LinkedIn: (add link)


