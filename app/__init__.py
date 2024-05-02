from flask import Flask
from .routes import init_routes
from .models import db

def create_app():
    app = Flask(__name__, 
                template_folder="../templates", 
                static_folder="../static")
    
    app.secret_key = 'supersecretkey'

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3.db'   
    db.init_app(app)

    # Initialize routes
    init_routes(app)
    
    with app.app_context():
        db.create_all()

    return app
