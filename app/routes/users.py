import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from app.models import db, User
import jwt
from app.models import User, karya_seni, ruang_video

users_bp = Blueprint("users", __name__)

UPLOAD_FOLDER = "static/uploads/profile_pictures"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


# ✅ Fungsi cek ekstensi file
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ Middleware verifikasi token
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


# ✅ Register user baru
@users_bp.route("/", methods=["POST"])
def register_user():
    data = request.form
    new_user = User(
        email=data["email"],
        username=data["username"],
        password=data["password"],
        nama_lengkap=data["nama_lengkap"],
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201


# ✅ Update user by ID (hanya jika JWT valid dan ID cocok)
@users_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_user(current_user, id):
    user = User.query.get_or_404(id)

    # Pastikan hanya pemilik akun yang bisa update dirinya
    if current_user.id != user.id:
        return jsonify({"message": "Tidak diizinkan mengedit user lain"}), 403

    data = request.form
    user.nama_lengkap = data.get("nama_lengkap", user.nama_lengkap)
    user.username = data.get("username", user.username)
    user.bio = data.get("bio", user.bio)
    user.lokasi = data.get("lokasi", user.lokasi)

    # Upload foto profil
    foto = request.files.get("foto_profil")
    if foto and allowed_file(foto.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(foto.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(filepath)
        user.foto_profil = filepath

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Profil berhasil diperbarui"})


# ✅ Ambil semua user
@users_bp.route("/", methods=["GET"])
def get_users():
    users = User.query.filter_by(deleted_at=None).all()
    result = []
    for user in users:
        result.append(
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "nama_lengkap": user.nama_lengkap,
                "bio": user.bio,
                "lokasi": user.lokasi,
                "created_at": user.created_at,
                "foto_profil": (
                    request.host_url.rstrip("/") + "/" + user.foto_profil
                    if user.foto_profil
                    else None
                ),
            }
        )
    return jsonify(result)


@users_bp.route("/username/<string:username>", methods=["GET"])
def get_user_by_username(username):
    #log
    print("🪪 Diterima username:", repr(username))  # Tambahkan ini
    user = User.query.filter_by(username=username, deleted_at=None).first()
    print("📄 Hasil query user:", user)
    user = User.query.filter_by(username=username, deleted_at=None).first()
    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    return jsonify(
        {
            "id": user.id,
            "email": user.email, 
            "username": user.username,
            "nama_lengkap": user.nama_lengkap,
            "bio": user.bio,
            "lokasi": user.lokasi,
            "foto_profil": (
                request.host_url.rstrip("/") + "/" + user.foto_profil
                if user.foto_profil
                else None
            ),
        }
    )


# # read seniman
# @users_bp.route("/<int:user_id>/detail", methods=["GET"])
# def get_seniman_detail(user_id):
#     user = User.query.filter_by(id=user_id, deleted_at=None).first()
#     if not user:
#         return jsonify({"message": "User tidak ditemukan"}), 404

#     karya_list = karya_seni.query.filter_by(user_id=user.id, deleted_at=None).all()
#     video_list = ruang_video.query.filter_by(user_id=user.id, deleted_at=None).all()

#     return jsonify(
#         {
#             "nama_lengkap": user.nama_lengkap,
#             "username": user.username,
#             "bio": user.bio,
#             "lokasi": user.lokasi,
#             "foto_profil": (
#                 request.host_url + user.foto_profil if user.foto_profil else None
#             ),
#             "karya_seni": [
#                 {
#                     "id": karya.id,
#                     "judul_karya": karya.judul_karya,
#                     "deskripsi": karya.deskripsi,
#                     "link_foto": karya.link_foto,
#                     "link_whatsapp": karya.link_whatsapp,
#                 }
#                 for karya in karya_list
#             ],
#             "ruang_video": [
#                 {
#                     "id": video.id,
#                     "judul": video.judul,
#                     "deskripsi": video.deskripsi,
#                     "link_youtube": video.link_youtube,
#                 }
#                 for video in video_list
#             ],
#         }
#     )

@users_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "nama_lengkap": current_user.nama_lengkap,
        "bio": current_user.bio,
        "lokasi": current_user.lokasi,
        "foto_profil": (
            request.host_url.rstrip("/") + "/" + current_user.foto_profil
            if current_user.foto_profil
            else None
        ),
        "created_at": current_user.created_at
    })


@users_bp.route("/<int:user_id>/detail", methods=["GET"])
def get_user_detail(user_id):
    try:
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return jsonify({"message": "User tidak ditemukan"}), 404

        karya_list = karya_seni.query.filter_by(user_id=user.id, deleted_at=None).all()
        video_list = ruang_video.query.filter_by(user_id=user.id, deleted_at=None).all()

        # Debug print
        print("📌 User:", user.username)
        print("🎨 Jumlah karya:", len(karya_list))
        print("📹 Jumlah video:", len(video_list))

        karya_data = [
            {
                "id": k.id,
                "judul_karya": k.judul_karya or "",
                "deskripsi": k.deskripsi or "",
                "link_foto": k.link_foto or "",
                "link_whatsapp": k.link_whatsapp or "",
                "photo": f"http://127.0.0.1:5000/{k.link_foto}" if k.link_foto else None,
            }
            for k in karya_list
        ]

        video_data = [
    {
        "id": v.id,
        "judul": v.judul or "",
        "deskripsi": v.deskripsi or "",
        "link_youtube": v.link_youtube or "",
        "link_thumbnail": v.link_thumbnail if v.link_thumbnail.startswith("http") else request.host_url.rstrip("/") + "/" + v.link_thumbnail,
        "title": v.judul or "",
        "description": v.deskripsi or "",
        "youtubeLink": v.link_youtube or "",
        "thumbnail": request.host_url.rstrip("/") + "/" + v.link_thumbnail if v.link_thumbnail else None,
    }
    for v in video_list
]


        return jsonify({
            "id": user.id,
            "username": user.username,
            "nama_lengkap": user.nama_lengkap,
            "bio": user.bio,
            "lokasi": user.lokasi,
            "foto_profil": request.host_url.rstrip("/") + "/" + user.foto_profil if user.foto_profil else None,
            "karya_seni": karya_data,
            "ruang_video": video_data
        })

    except Exception as e:
        print("🔥 ERROR di /<user_id>/detail:", e)
        return jsonify({"error": str(e)}), 500

