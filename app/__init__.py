from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv()  # Load .env file
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # satu level di atas app/
    static_folder_path = os.path.join(base_dir, 'static')

    app = Flask(__name__,
                static_folder=static_folder_path,
                static_url_path='/static')

    # Load configurations
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY  # ✅ Simpan kunci rahasia

    # ✅ Inisialisasi CORS untuk semua route /api/*
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,  # ✅ penting jika pakai token Authorization
        expose_headers=["Content-Type", "Authorization"],  # ✅ jika ingin header tertentu terlihat
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ agar OPTIONS tidak diblok
    )

    # Inisialisasi DB dan migrasi
    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    # Register blueprints
    from app.routes.users import users_bp
    from app.routes.karyaseni import karya_seni_bp
    from app.routes.ruangvideo import ruang_video_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(karya_seni_bp, url_prefix="/api/karya_seni")
    app.register_blueprint(ruang_video_bp, url_prefix="/api/ruang_video")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
