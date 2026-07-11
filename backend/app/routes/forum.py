from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import ForumThread, ForumReply, User

forum_bp = Blueprint("forum", __name__)

CATEGORIES = ["General", "Web Development", "Programming", "Digital Marketing", "Data Science", "Career Help"]


@forum_bp.route("/categories", methods=["GET"])
def categories():
    return jsonify({"categories": CATEGORIES}), 200


@forum_bp.route("/threads", methods=["GET"])
def list_threads():
    category = request.args.get("category")
    query = ForumThread.query
    if category and category != "All":
        query = query.filter_by(category=category)
    threads = query.order_by(ForumThread.created_at.desc()).all()

    result = []
    for t in threads:
        reply_count = ForumReply.query.filter_by(thread_id=t.id).count()
        author = User.query.get(t.user_id)
        result.append({
            "id": t.id, "title": t.title, "body": t.body, "category": t.category,
            "author_name": author.name if author else "Unknown",
            "reply_count": reply_count, "created_at": t.created_at.isoformat(),
        })
    return jsonify({"threads": result}), 200


@forum_bp.route("/threads", methods=["POST"])
@jwt_required()
def create_thread():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()
    category = data.get("category") or "General"

    if not title or not body:
        return jsonify({"error": "title and body are required"}), 400
    if category not in CATEGORIES:
        category = "General"

    thread = ForumThread(user_id=user_id, title=title, body=body, category=category)
    db.session.add(thread)
    db.session.commit()
    return jsonify({"message": "Thread created", "thread_id": thread.id}), 201


@forum_bp.route("/threads/<int:thread_id>", methods=["GET"])
def get_thread(thread_id):
    thread = ForumThread.query.get(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    author = User.query.get(thread.user_id)
    replies = ForumReply.query.filter_by(thread_id=thread_id).order_by(ForumReply.created_at.asc()).all()
    reply_data = []
    for r in replies:
        r_author = User.query.get(r.user_id)
        reply_data.append({
            "id": r.id, "body": r.body, "author_name": r_author.name if r_author else "Unknown",
            "created_at": r.created_at.isoformat(),
        })

    return jsonify({"thread": {
        "id": thread.id, "title": thread.title, "body": thread.body, "category": thread.category,
        "author_name": author.name if author else "Unknown", "created_at": thread.created_at.isoformat(),
        "replies": reply_data,
    }}), 200


@forum_bp.route("/threads/<int:thread_id>/replies", methods=["POST"])
@jwt_required()
def add_reply(thread_id):
    user_id = get_jwt_identity()
    thread = ForumThread.query.get(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"error": "body is required"}), 400

    reply = ForumReply(thread_id=thread_id, user_id=user_id, body=body)
    db.session.add(reply)
    db.session.commit()

    # Notify the thread's original author (if someone else replied)
    if str(thread.user_id) != str(user_id):
        from app.routes.notifications import create_notification
        replier = User.query.get(user_id)
        create_notification(thread.user_id, f"{replier.name if replier else 'Someone'} replied to your thread \"{thread.title}\"")

    return jsonify({"message": "Reply posted", "reply_id": reply.id}), 201
