from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

from app.models import db, User  # pastikan ini sesuai dengan struktur kamu
from config import Config  # buat SECRET_KEY di file config.py

auth_bp = Blueprint("auth", __name__)

secret_key = Config.SECRET_KEY


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    nama_lengkap = data.get("nama_lengkap")
    bio = data.get("bio")
    lokasi = data.get("lokasi")

    # Validasi minimal
    if not all([email, username, password, nama_lengkap]):
        return (
            jsonify(
                {"message": "Email, username, password, dan nama_lengkap wajib diisi"}
            ),
            400,
        )

    # Cek user sudah ada
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({"message": "User sudah terdaftar"}), 409

    hashed_pw = generate_password_hash(password)

    new_user = User(
        email=email,
        username=username,
        password=hashed_pw,
        nama_lengkap=nama_lengkap,
        bio=bio,
        lokasi=lokasi,
        created_at=datetime.utcnow(),
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Email atau password salah"}), 401

    payload = {"user_id": user.id, "exp": datetime.utcnow() + timedelta(days=1)}
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    return jsonify({
    "success": True,
    "token": token,
    "user": {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nama_lengkap": user.nama_lengkap,
        "foto_profil": user.foto_profil,
        "bio": user.bio,
        "lokasi": user.lokasi
    }
}), 200
