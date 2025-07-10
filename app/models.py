from app import db
from datetime import datetime
from flask import Blueprint, request, jsonify


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    foto_profil = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    lokasi = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)


class karya_seni(db.Model):
    __tablename__ = "karya_seni"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    judul_karya = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    link_foto = db.Column(db.String(255), nullable=False)
    link_whatsapp = db.Column(db.String(255), nullable=True)
    like_count = db.Column(db.Integer, default=0) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "judul_karya": self.judul_karya,
            "deskripsi": self.deskripsi,
            "link_foto": self.link_foto,
            "link_whatsapp": self.link_whatsapp,
            "like_count": self.like_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ruang_video(db.Model):
    __tablename__ = "ruang_video"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    judul = db.Column(db.String(100), nullable=False)
    link_youtube = db.Column(db.String(255), nullable=False)
    link_thumbnail = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    dibuat_oleh = db.Column(db.String(100), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)


class LikeVideo(db.Model):
    __tablename__ = "like_video"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("ruang_video.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
