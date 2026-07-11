from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.models import User, ChatMessage

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/contacts", methods=["GET"])
@jwt_required()
def contacts():
    """Anyone can message anyone on the platform (mentors, students, admins) —
    simplest model for a CSP project. Returns everyone except yourself."""
    user_id = get_jwt_identity()
    users = User.query.filter(User.id != user_id).order_by(User.name).all()
    return jsonify({"contacts": [
        {"id": u.id, "name": u.name, "role": u.role, "avatar_url": u.avatar_url} for u in users
    ]}), 200


@chat_bp.route("/history/<int:other_user_id>", methods=["GET"])
@jwt_required()
def history(other_user_id):
    user_id = int(get_jwt_identity())
    messages = ChatMessage.query.filter(
        or_(
            (ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == other_user_id),
            (ChatMessage.sender_id == other_user_id) & (ChatMessage.receiver_id == user_id),
        )
    ).order_by(ChatMessage.sent_at.asc()).all()

    return jsonify({"messages": [
        {
            "id": m.id, "sender_id": m.sender_id, "receiver_id": m.receiver_id,
            "message": m.message, "sent_at": m.sent_at.isoformat(),
            "is_mine": m.sender_id == user_id,
        } for m in messages
    ]}), 200
