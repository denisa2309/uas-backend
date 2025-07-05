import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import karya_seni, User
import jwt
from functools import wraps
from pytz import timezone, utc

karya_seni_bp = Blueprint("karyaseni", __name__)
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
WITA = timezone("Asia/Makassar")


# Fungsi bantu untuk konversi UTC ke WITA
def utc_to_wita(dt_utc):
    if dt_utc:
        return utc.localize(dt_utc).astimezone(WITA).strftime("%Y-%m-%d %H:%M:%S")
    return None


# Middleware token
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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ CORS Preflight handler untuk POST /api/karya_seni
@karya_seni_bp.route("/", methods=["OPTIONS"])
def preflight_karya():
    return '', 200


# ✅ CREATE
@karya_seni_bp.route("", methods=["POST"])
@token_required
def create_karya(current_user):
    try:
        data = request.form
        foto = request.files.get("link_foto")

        if not foto or not allowed_file(foto.filename):
            return jsonify({"error": "File foto tidak valid"}), 400

        filename = secure_filename(foto.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(filepath)

        new_karya = karya_seni(
            user_id=current_user.id,
            judul_karya=data.get("judul_karya"),
            deskripsi=data.get("deskripsi"),
            link_foto=filepath,
            link_whatsapp=data.get("link_whatsapp"),
            created_at=datetime.utcnow(),
        )

        db.session.add(new_karya)
        db.session.commit()
        return jsonify({"message": "Karya seni berhasil ditambahkan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ READ (public)
@karya_seni_bp.route("", methods=["GET"])
def get_all_karya():
    karya_list = karya_seni.query.filter_by(deleted_at=None).all()
    results = []
    for karya in karya_list:
        results.append({
            "id": karya.id,
            "user_id": karya.user_id,
            "judul_karya": karya.judul_karya,
            "deskripsi": karya.deskripsi,
            "link_foto": karya.link_foto,
            "link_whatsapp": karya.link_whatsapp,
            "created_at": utc_to_wita(karya.created_at),
            "updated_at": utc_to_wita(karya.updated_at),
        })
    return jsonify(results)


# ✅ UPDATE
@karya_seni_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_karya(current_user, id):
    karya = karya_seni.query.get_or_404(id)
    if karya.user_id != current_user.id:
        return jsonify({"message": "Tidak boleh edit karya milik orang lain"}), 403

    data = request.form
    karya.judul_karya = data.get("judul_karya", karya.judul_karya)
    karya.deskripsi = data.get("deskripsi", karya.deskripsi)
    karya.link_whatsapp = data.get("link_whatsapp", karya.link_whatsapp)
    karya.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Karya seni berhasil diperbarui"})


# ✅ DELETE
@karya_seni_bp.route("/<int:id>", methods=["DELETE"])
@token_required
def delete_karya(current_user, id):
    karya = karya_seni.query.get_or_404(id)
    if karya.user_id != current_user.id:
        return jsonify({"message": "Tidak boleh hapus karya milik orang lain"}), 403

    karya.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Karya seni berhasil dihapus (soft delete)"})
