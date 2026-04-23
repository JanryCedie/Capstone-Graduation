from flask import Flask, send_from_directory
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.finance import finance_bp

def create_app():
    # Configure Flask to serve static files from the frontend build directory
    frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'dist')
    app = Flask(__name__, static_folder=frontend_dist)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})
    JWTManager(app)
    
    # Ensure instance folder exists for SQLite
    os.makedirs(app.instance_path, exist_ok=True)
    
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')

    # Serve the React App - Catch-all Route
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        print(f"DEBUG: serving path='{path}' from static_folder='{app.static_folder}'")
        full_path = os.path.join(app.static_folder, path)
        if path != "" and os.path.exists(full_path):
            return send_from_directory(app.static_folder, path)
        else:
            if os.path.exists(os.path.join(app.static_folder, 'index.html')):
                return send_from_directory(app.static_folder, 'index.html')
            return "Frontend build not found.", 404

    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print(" EcoConnect is running at http://localhost:8000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8000)
