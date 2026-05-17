from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional

# Setup app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///xbox_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup database
db = SQLAlchemy(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== DATABASE MODELS ====================

# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id: int = db.mapped_column(db.Integer, primary_key=True)
    username: str = db.mapped_column(db.String(80), unique=True, nullable=False)
    email: str = db.mapped_column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.mapped_column(db.String(200), nullable=False)
    created_at: datetime = db.mapped_column(db.DateTime, default=datetime.now)
    
    def set_password(self, pwd: str) -> None:
        """Hash password"""
        self.password_hash = generate_password_hash(pwd, method='pbkdf2:sha256')
    
    def check_password(self, pwd: str) -> bool:
        """Check password"""
        return check_password_hash(self.password_hash, pwd)

# Xbox console model
class Console(db.Model):
    __tablename__ = 'console'
    id: int = db.mapped_column(db.Integer, primary_key=True)
    name: str = db.mapped_column(db.String(100), nullable=False)
    year: int = db.mapped_column(db.Integer, nullable=False)
    cpu: Optional[str] = db.mapped_column(db.String(200))
    ram: Optional[str] = db.mapped_column(db.String(100))
    storage: Optional[str] = db.mapped_column(db.String(100))
    description: Optional[str] = db.mapped_column(db.Text)
    games = db.relationship('Game', backref='console', lazy=True, cascade='all, delete-orphan')
    
    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'cpu': self.cpu,
            'ram': self.ram,
            'storage': self.storage,
            'description': self.description
        }

# Xbox game model
class Game(db.Model):
    __tablename__ = 'game'
    id: int = db.mapped_column(db.Integer, primary_key=True)
    title: str = db.mapped_column(db.String(150), nullable=False)
    console_id: int = db.mapped_column(db.Integer, db.ForeignKey('console.id'), nullable=False)
    year: int = db.mapped_column(db.Integer, nullable=False)
    maker: Optional[str] = db.mapped_column(db.String(150))
    kind: Optional[str] = db.mapped_column(db.String(100))
    score: float = db.mapped_column(db.Float, default=5.0)
    description: Optional[str] = db.mapped_column(db.Text)
    created_at: datetime = db.mapped_column(db.DateTime, default=datetime.now)
    favorites = db.relationship('Favorite', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def to_json(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'console_id': self.console_id,
            'year': self.year,
            'maker': self.maker,
            'kind': self.kind,
            'score': self.score,
            'description': self.description
        }

# Favorite games model
class Favorite(db.Model):
    __tablename__ = 'favorite'
    id: int = db.mapped_column(db.Integer, primary_key=True)
    user_id: int = db.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id: int = db.mapped_column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    added_at: datetime = db.mapped_column(db.DateTime, default=datetime.now)
    user = db.relationship('User', backref='favorites')

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return db.session.get(User, int(user_id))

# ==================== SETUP DATA ====================

def add_data() -> None:
    """Initialize database with sample data"""
    # Add consoles if they don't exist
    if db.session.query(Console).first() is None:
        c1 = Console(
            name='Xbox',
            year=2001,
            cpu='Intel Pentium III 733MHz',
            ram='64 MB',
            storage='8 GB',
            description='The original Xbox console'
        )
        c2 = Console(
            name='Xbox 360',
            year=2005,
            cpu='Xenon 3.2GHz',
            ram='512 MB',
            storage='20 GB',
            description='The second generation Xbox'
        )
        c3 = Console(
            name='Xbox One',
            year=2013,
            cpu='AMD 8-core 1.75GHz',
            ram='8 GB',
            storage='500 GB',
            description='The third generation Xbox'
        )
        c4 = Console(
            name='Xbox Series X',
            year=2020,
            cpu='AMD 8-core 3.8GHz',
            ram='16 GB',
            storage='1024 GB',
            description='The newest Xbox console'
        )
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()
        
        # Add games
        g1 = Game(
            title='Halo: Combat Evolved',
            console_id=1,
            year=2001,
            maker='Bungie',
            kind='First Person Shooter',
            score=9.7,
            description='The game that made Xbox famous'
        )
        g2 = Game(
            title='Halo 2',
            console_id=2,
            year=2004,
            maker='Bungie',
            kind='First Person Shooter',
            score=9.5,
            description='The epic sequel'
        )
        g3 = Game(
            title='Gears of War',
            console_id=2,
            year=2006,
            maker='Epic Games',
            kind='Third Person Shooter',
            score=9.4,
            description='A gritty shooter classic'
        )
        g4 = Game(
            title='Halo Infinite',
            console_id=4,
            year=2021,
            maker='343 Industries',
            kind='First Person Shooter',
            score=8.9,
            description='The latest Halo game'
        )
        g5 = Game(
            title='Forza Horizon 5',
            console_id=4,
            year=2021,
            maker='Playground Games',
            kind='Racing',
            score=9.2,
            description='Amazing racing game'
        )
        g6 = Game(
            title='Minecraft',
            console_id=4,
            year=2011,
            maker='Mojang',
            kind='Sandbox',
            score=9.0,
            description='Build whatever you want'
        )
        
        db.session.add_all([g1, g2, g3, g4, g5, g6])
        db.session.commit()

# ==================== WEB ROUTES ====================

@app.route('/')
def home() -> str:
    """Homepage with stats"""
    total_c = db.session.query(Console).count()
    total_g = db.session.query(Game).count()
    
    # Count average score manually like a beginner would
    all_games = db.session.query(Game).all()
    total_score = 0
    for g in all_games:
        total_score = total_score + g.score
    
    if len(all_games) > 0:
        avg_score = total_score / len(all_games)
    else:
        avg_score = 0
    
    return render_template('home.html', consoles=total_c, games=total_g, avg=round(avg_score, 1))

@app.route('/consoles')
def consoles() -> str:
    """List all consoles"""
    all_consoles = db.session.query(Console).all()
    return render_template('consoles.html', consoles=all_consoles)

@app.route('/console/<int:c_id>')
def console_detail(c_id: int) -> tuple[str, int]:
    """Show single console details"""
    c = db.session.get(Console, c_id)
    if c is None:
        return "Console not found", 404
    games_list = db.session.query(Game).filter_by(console_id=c_id).all()
    return render_template('console_detail.html', console=c, games=games_list)

@app.route('/games')
def games() -> str:
    """List all games with pagination"""
    page = request.args.get('page', 1, type=int)
    all_games = db.session.query(Game).all()
    
    # Simple pagination like a beginner would do it
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    games_list = all_games[start:end]
    
    total_pages = (len(all_games) + per_page - 1) // per_page
    
    return render_template('games.html', games=games_list, page=page, total_pages=total_pages)

@app.route('/game/<int:g_id>')
def game_detail(g_id: int) -> tuple[str, int]:
    """Show single game details"""
    g = db.session.get(Game, g_id)
    if g is None:
        return "Game not found", 404
    c = db.session.get(Console, g.console_id)
    return render_template('game_detail.html', game=g, console=c)

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register() -> str | tuple[str, int]:
    """Register new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        # Check if user exists
        user = db.session.query(User).filter_by(username=username).first()
        if user is not None:
            return "Username already exists!", 400
        
        # Check if email exists
        user2 = db.session.query(User).filter_by(email=email).first()
        if user2 is not None:
            return "Email already exists!", 400
        
        # Check password match
        if password != password2:
            return "Passwords do not match!", 400
        
        # Check password length
        if len(password) < 6:
            return "Password must be at least 6 characters!", 400
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect('/')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login() -> str | tuple[str, int]:
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.session.query(User).filter_by(username=username).first()
        
        if user is None:
            return "User not found!", 400
        
        if not user.check_password(password):
            return "Wrong password!", 400
        
        login_user(user)
        return redirect('/')
    
    return render_template('login.html')

@app.route('/logout')
def logout() -> str:
    """User logout"""
    logout_user()
    return redirect('/')

# ==================== REST API ROUTES ====================

# Get all consoles as JSON
@app.route('/api/consoles', methods=['GET'])
def api_get_consoles() -> tuple[str, int]:
    """REST API - Get all consoles"""
    all_consoles = db.session.query(Console).all()
    result = []
    for c in all_consoles:
        result.append(c.to_json())
    return jsonify(result), 200

# Get single console as JSON
@app.route('/api/consoles/<int:c_id>', methods=['GET'])
def api_get_console(c_id: int) -> tuple[str, int]:
    """REST API - Get single console"""
    c = db.session.get(Console, c_id)
    if c is None:
        return jsonify({'error': 'Console not found'}), 404
    return jsonify(c.to_json()), 200

# Create new console (need to be logged in)
@app.route('/api/consoles', methods=['POST'])
@login_required
def api_create_console() -> tuple[str, int]:
    """REST API - Create console"""
    data = request.get_json()
    
    if 'name' not in data or 'year' not in data:
        return jsonify({'error': 'Missing name or year'}), 400
    
    new_console = Console(
        name=data['name'],
        year=data['year'],
        cpu=data.get('cpu'),
        ram=data.get('ram'),
        storage=data.get('storage'),
        description=data.get('description')
    )
    db.session.add(new_console)
    db.session.commit()
    
    return jsonify(new_console.to_json()), 201

# Update console
@app.route('/api/consoles/<int:c_id>', methods=['PUT'])
@login_required
def api_update_console(c_id: int) -> tuple[str, int]:
    """REST API - Update console"""
    c = db.session.get(Console, c_id)
    if c is None:
        return jsonify({'error': 'Console not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        c.name = data['name']
    if 'year' in data:
        c.year = data['year']
    if 'cpu' in data:
        c.cpu = data['cpu']
    if 'ram' in data:
        c.ram = data['ram']
    if 'storage' in data:
        c.storage = data['storage']
    if 'description' in data:
        c.description = data['description']
    
    db.session.commit()
    return jsonify(c.to_json()), 200

# Delete console
@app.route('/api/consoles/<int:c_id>', methods=['DELETE'])
@login_required
def api_delete_console(c_id: int) -> tuple[str, int]:
    """REST API - Delete console"""
    c = db.session.get(Console, c_id)
    if c is None:
        return jsonify({'error': 'Console not found'}), 404
    
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Console deleted'}), 200

# Get all games as JSON
@app.route('/api/games', methods=['GET'])
def api_get_games() -> tuple[str, int]:
    """REST API - Get all games"""
    all_games = db.session.query(Game).all()
    result = []
    for g in all_games:
        result.append(g.to_json())
    return jsonify(result), 200

# Get single game as JSON
@app.route('/api/games/<int:g_id>', methods=['GET'])
def api_get_game(g_id: int) -> tuple[str, int]:
    """REST API - Get single game"""
    g = db.session.get(Game, g_id)
    if g is None:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(g.to_json()), 200

# Create new game
@app.route('/api/games', methods=['POST'])
@login_required
def api_create_game() -> tuple[str, int]:
    """REST API - Create game"""
    data = request.get_json()
    
    if 'title' not in data or 'console_id' not in data or 'year' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if console exists
    c = db.session.get(Console, data['console_id'])
    if c is None:
        return jsonify({'error': 'Console not found'}), 404
    
    new_game = Game(
        title=data['title'],
        console_id=data['console_id'],
        year=data['year'],
        maker=data.get('maker'),
        kind=data.get('kind'),
        score=data.get('score', 5.0),
        description=data.get('description')
    )
    db.session.add(new_game)
    db.session.commit()
    
    return jsonify(new_game.to_json()), 201

# Update game
@app.route('/api/games/<int:g_id>', methods=['PUT'])
@login_required
def api_update_game(g_id: int) -> tuple[str, int]:
    """REST API - Update game"""
    g = db.session.get(Game, g_id)
    if g is None:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        g.title = data['title']
    if 'year' in data:
        g.year = data['year']
    if 'maker' in data:
        g.maker = data['maker']
    if 'kind' in data:
        g.kind = data['kind']
    if 'score' in data:
        g.score = data['score']
    if 'description' in data:
        g.description = data['description']
    
    db.session.commit()
    return jsonify(g.to_json()), 200

# Delete game
@app.route('/api/games/<int:g_id>', methods=['DELETE'])
@login_required
def api_delete_game(g_id: int) -> tuple[str, int]:
    """REST API - Delete game"""
    g = db.session.get(Game, g_id)
    if g is None:
        return jsonify({'error': 'Game not found'}), 404
    
    db.session.delete(g)
    db.session.commit()
    return jsonify({'message': 'Game deleted'}), 200

# Get all games by console
@app.route('/api/consoles/<int:c_id>/games', methods=['GET'])
def api_get_console_games(c_id: int) -> tuple[str, int]:
    """REST API - Get games for console"""
    games_list = db.session.query(Game).filter_by(console_id=c_id).all()
    result = []
    for g in games_list:
        result.append(g.to_json())
    return jsonify(result), 200

# Add game to favorites
@app.route('/api/favorites', methods=['POST'])
@login_required
def api_add_favorite() -> tuple[str, int]:
    """REST API - Add to favorites"""
    data = request.get_json()
    game_id = data.get('game_id')
    
    # Check if game exists
    g = db.session.get(Game, game_id)
    if g is None:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if already in favorites
    fav = db.session.query(Favorite).filter_by(user_id=current_user.id, game_id=game_id).first()
    if fav is not None:
        return jsonify({'error': 'Already in favorites'}), 400
    
    # Add to favorites
    new_fav = Favorite(user_id=current_user.id, game_id=game_id)
    db.session.add(new_fav)
    db.session.commit()
    
    return jsonify({'message': 'Added to favorites'}), 201

# Get user favorites
@app.route('/api/favorites', methods=['GET'])
@login_required
def api_get_favorites() -> tuple[str, int]:
    """REST API - Get favorites"""
    favs = db.session.query(Favorite).filter_by(user_id=current_user.id).all()
    result = []
    for fav in favs:
        result.append({
            'id': fav.id,
            'game': fav.game.to_json(),
            'added_at': str(fav.added_at)
        })
    return jsonify(result), 200

# Remove from favorites
@app.route('/api/favorites/<int:fav_id>', methods=['DELETE'])
@login_required
def api_remove_favorite(fav_id: int) -> tuple[str, int]:
    """REST API - Remove from favorites"""
    fav = db.session.get(Favorite, fav_id)
    if fav is None:
        return jsonify({'error': 'Favorite not found'}), 404
    
    if fav.user_id != current_user.id:
        return jsonify({'error': 'Not your favorite'}), 403
    
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Removed from favorites'}), 200

# Get stats
@app.route('/api/stats', methods=['GET'])
def api_get_stats() -> tuple[str, int]:
    """REST API - Get statistics"""
    total_consoles = db.session.query(Console).count()
    total_games = db.session.query(Game).count()
    
    all_games = db.session.query(Game).all()
    total_score = 0
    for g in all_games:
        total_score = total_score + g.score
    
    if len(all_games) > 0:
        avg_score = total_score / len(all_games)
    else:
        avg_score = 0
    
    return jsonify({
        'total_consoles': total_consoles,
        'total_games': total_games,
        'average_score': round(avg_score, 1)
    }), 200

# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(error) -> tuple[str, int]:
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error) -> tuple[str, int]:
    return render_template('500.html'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_data()
    
    # Use Python 3.12+ syntax
    app.run(debug=True, host='0.0.0.0', port=5000)
