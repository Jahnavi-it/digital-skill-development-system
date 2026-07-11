from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__)


def create_notification(user_id, message):
    """Shared helper — any module (forum, chat, gamification, ...) calls this
    to both persist a notification and push it live over WebSocket if the
    user is currently connected."""
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()

    try:
        from app import socketio
        socketio.emit("notification", {
            "id": notif.id, "message": notif.message, "created_at": notif.created_at.isoformat(),
        }, room=f"user_{user_id}")
    except Exception:
        pass  # socket layer being unavailable should never break the REST request

    return notif


@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = get_jwt_identity()
    items = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify({
        "notifications": [
            {"id": n.id, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat()}
            for n in items
        ],
        "unread_count": Notification.query.filter_by(user_id=user_id, is_read=False).count(),
    }), 200


@notifications_bp.route("/<int:notif_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(notif_id):
    user_id = get_jwt_identity()
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if not notif:
        return jsonify({"error": "Notification not found"}), 404
    notif.is_read = True
    db.session.commit()
    return jsonify({"message": "Marked as read"}), 200


@notifications_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"}), 200
