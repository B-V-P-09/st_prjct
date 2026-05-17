# 🎮 Xbox History Project

A Flask web application with REST API built by a 10th grader learning Python!

## Features

✅ **User Authentication** - Login & Registration with Flask-Login
✅ **ORM Models** - SQLAlchemy for database management
✅ **REST API** - Full CRUD operations for Consoles, Games & Favorites
✅ **Web Routes** - Beautiful Xbox-themed interface
✅ **Bootstrap Styling** - Responsive dark mode design
✅ **~550 Lines** - Beginner-friendly Python code

## Requirements

- Python 3.12+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Werkzeug 3.0.1

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Visit: **http://localhost:5000**

## API Endpoints

### Consoles
- `GET /api/consoles` - Get all consoles
- `GET /api/consoles/<id>` - Get single console
- `POST /api/consoles` - Create console (requires login)
- `PUT /api/consoles/<id>` - Update console (requires login)
- `DELETE /api/consoles/<id>` - Delete console (requires login)

### Games
- `GET /api/games` - Get all games
- `GET /api/games/<id>` - Get single game
- `POST /api/games` - Create game (requires login)
- `PUT /api/games/<id>` - Update game (requires login)
- `DELETE /api/games/<id>` - Delete game (requires login)
- `GET /api/consoles/<id>/games` - Get games by console

### Favorites
- `GET /api/favorites` - Get user favorites (requires login)
- `POST /api/favorites` - Add to favorites (requires login)
- `DELETE /api/favorites/<id>` - Remove from favorites (requires login)

### Statistics
- `GET /api/stats` - Get stats (consoles, games, average rating)

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── consoles.html     # Consoles list
│   ├── console_detail.html # Single console
│   ├── games.html        # Games list
│   ├── game_detail.html  # Single game
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── 404.html          # 404 error
│   └── 500.html          # 500 error
└── xbox_history.db       # SQLite database (auto-created)
```

## Database Models

### User
- id, username, email, password_hash, created_at

### Console
- id, name, year, cpu, ram, storage, description

### Game
- id, title, console_id, year, maker, kind, score, description, created_at

### Favorite
- id, user_id, game_id, added_at

## Made with ❤️ by a 10th Grader Learning Python 🐍
