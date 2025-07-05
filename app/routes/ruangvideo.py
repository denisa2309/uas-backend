import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import ruang_video, User
import jwt
from functools import wraps
from pytz import timezone, utc
from flask_cors import cross_origin

ruang_video_bp = Blueprint("ruangvideo", __name__)
WITA = timezone("Asia/Makassar")


# JWT middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token tidak ditemukan"}), 401
        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.get(data["user_id"])
            if not current_user or current_user.deleted_at:
                return jsonify({"message": "User tidak valid"}), 401
        except Exception as e:
            return jsonify({"message": f"Token tidak valid: {str(e)}"}), 401
        return f(current_user, *args, **kwargs)

    return decorated


def utc_to_wita(dt_utc):
    if dt_utc:
        return utc.localize(dt_utc).astimezone(WITA).strftime("%Y-%m-%d %H:%M:%S")
    return None


# ✅ CREATE
@ruang_video_bp.route("", methods=["POST"])
@cross_origin(origin="http://localhost:5173")
@token_required
def create_video(current_user):
    
    try:
        data = request.get_json()

        # Ambil data dari form
        judul = data.get("judul")
        link_youtube = data.get("link_youtube")
        link_thumbnail = data.get("link_thumbnail")
        deskripsi = data.get("deskripsi")
        dibuat_oleh = data.get("dibuat_oleh")

        # Validasi field penting
        if not judul or not link_youtube or not link_thumbnail or not dibuat_oleh:
            return (
                jsonify(
                    {
                        "error": "Field judul, link_youtube, link_thumbnail, dan dibuat_oleh wajib diisi"
                    }
                ),
                400,
            )

        new_video = ruang_video(
            user_id=current_user.id,
            judul=judul,
            deskripsi=deskripsi,
            link_youtube=link_youtube,
            link_thumbnail=link_thumbnail,
            dibuat_oleh=dibuat_oleh,
            created_at=datetime.utcnow(),
        )

        db.session.add(new_video)
        db.session.commit()
        return jsonify({"message": "Video berhasil ditambahkan"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ READ (public)
@ruang_video_bp.route("", methods=["GET"])
def get_all_video():
    videos = ruang_video.query.filter_by(deleted_at=None).all()
    results = []
    for v in videos:
        results.append(
            {
                "id": v.id,
                "user_id": v.user_id,
                "judul": v.judul,
                "link_youtube": v.link_youtube,
                "link_thumbnail": v.link_thumbnail,
                "deskripsi": v.deskripsi,
                "dibuat_oleh": v.dibuat_oleh,
                "created_at": utc_to_wita(v.created_at),
                "updated_at": utc_to_wita(v.updated_at),
            }
        )
    return jsonify(results)


# ✅ UPDATE
@ruang_video_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_video(current_user, id):
    video = ruang_video.query.get_or_404(id)
    if video.user_id != current_user.id:
        return jsonify({"message": "Tidak boleh edit video milik orang lain"}), 403

    data = request.form
    video.judul = data.get("judul", video.judul)
    video.link_youtube = data.get("link_youtube", video.link_youtube)
    video.link_thumbnail = data.get("link_thumbnail", video.link_thumbnail)
    video.deskripsi = data.get("deskripsi", video.deskripsi)
    video.dibuat_oleh = data.get("dibuat_oleh", video.dibuat_oleh)
    video.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Video berhasil diperbarui"})


# ✅ DELETE
@ruang_video_bp.route("/<int:id>", methods=["DELETE"])
@token_required
def delete_video(current_user, id):
    video = ruang_video.query.get_or_404(id)
    if video.user_id != current_user.id:
        return jsonify({"message": "Tidak boleh hapus video milik orang lain"}), 403

    video.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Video berhasil dihapus (soft delete)"})
