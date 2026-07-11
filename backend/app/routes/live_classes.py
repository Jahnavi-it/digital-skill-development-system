import secrets
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import LiveClass, Course, Enrollment, User

live_classes_bp = Blueprint("live_classes", __name__)


def _class_dict(lc):
    return {
        "id": lc.id,
        "course_id": lc.course_id,
        "course_title": lc.course.title if lc.course else None,
        "mentor_id": lc.mentor_id,
        "mentor_name": lc.mentor.name if lc.mentor else None,
        "title": lc.title,
        "scheduled_at": lc.scheduled_at.isoformat() if lc.scheduled_at else None,
        "room_code": lc.room_code,
        "status": lc.status,
    }


@live_classes_bp.route("", methods=["GET"])
@jwt_required()
def list_live_classes():
    """Returns upcoming/live classes for courses the current user is
    enrolled in (students) or teaches (mentors). Admins see everything."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    query = LiveClass.query
    if user.role == "mentor":
        query = query.filter_by(mentor_id=user_id)
    elif user.role != "admin":
        enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(user_id=user_id).all()]
        query = query.filter(LiveClass.course_id.in_(enrolled_course_ids)) if enrolled_course_ids else query.filter(False)

    items = query.order_by(LiveClass.scheduled_at.asc()).all()
    return jsonify({"live_classes": [_class_dict(lc) for lc in items]}), 200


@live_classes_bp.route("", methods=["POST"])
@jwt_required()
def schedule_live_class():
    """Mentors (and admins) schedule a new live class for one of their courses."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in ("mentor", "admin"):
        return jsonify({"error": "Only mentors can schedule live classes"}), 403

    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    title = (data.get("title") or "").strip()
    scheduled_at_raw = data.get("scheduled_at")

    if not course_id or not title or not scheduled_at_raw:
        return jsonify({"error": "course_id, title and scheduled_at are required"}), 400

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    if user.role == "mentor" and course.mentor_id != int(user_id):
        return jsonify({"error": "You can only schedule classes for your own courses"}), 403

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_raw)
    except ValueError:
        return jsonify({"error": "scheduled_at must be an ISO datetime, e.g. 2026-07-15T18:00"}), 400

    lc = LiveClass(
        course_id=course_id,
        mentor_id=user_id,
        title=title,
        scheduled_at=scheduled_at,
        room_code=secrets.token_urlsafe(9),
        status="scheduled",
    )
    db.session.add(lc)
    db.session.commit()

    # notify every enrolled student
    from app.routes.notifications import create_notification
    for e in Enrollment.query.filter_by(course_id=course_id).all():
        create_notification(e.user_id, f"New live class scheduled: {title}")

    return jsonify({"message": "Live class scheduled", "live_class": _class_dict(lc)}), 201


@live_classes_bp.route("/<int:class_id>", methods=["GET"])
@jwt_required()
def get_live_class(class_id):
    lc = LiveClass.query.get(class_id)
    if not lc:
        return jsonify({"error": "Live class not found"}), 404
    return jsonify({"live_class": _class_dict(lc)}), 200


@live_classes_bp.route("/<int:class_id>/start", methods=["PUT"])
@jwt_required()
def start_live_class(class_id):
    user_id = get_jwt_identity()
    lc = LiveClass.query.get(class_id)
    if not lc:
        return jsonify({"error": "Live class not found"}), 404
    if lc.mentor_id != int(user_id):
        return jsonify({"error": "Only the hosting mentor can start this class"}), 403

    lc.status = "live"
    db.session.commit()

    from app.routes.notifications import create_notification
    for e in Enrollment.query.filter_by(course_id=lc.course_id).all():
        create_notification(e.user_id, f"Live class \"{lc.title}\" has started — join now!")

    return jsonify({"message": "Class is now live", "live_class": _class_dict(lc)}), 200


@live_classes_bp.route("/<int:class_id>/end", methods=["PUT"])
@jwt_required()
def end_live_class(class_id):
    user_id = get_jwt_identity()
    lc = LiveClass.query.get(class_id)
    if not lc:
        return jsonify({"error": "Live class not found"}), 404
    if lc.mentor_id != int(user_id):
        return jsonify({"error": "Only the hosting mentor can end this class"}), 403

    lc.status = "ended"
    db.session.commit()
    return jsonify({"message": "Class ended", "live_class": _class_dict(lc)}), 200


@live_classes_bp.route("/<int:class_id>/join", methods=["GET"])
@jwt_required()
def join_live_class(class_id):
    """Returns the room_code needed to enter the video call, after checking
    the requester is either the hosting mentor or enrolled in the course."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    lc = LiveClass.query.get(class_id)
    if not lc:
        return jsonify({"error": "Live class not found"}), 404

    is_host = lc.mentor_id == int(user_id)
    is_enrolled = Enrollment.query.filter_by(user_id=user_id, course_id=lc.course_id).first() is not None
    if not (is_host or is_enrolled or user.role == "admin"):
        return jsonify({"error": "You must be enrolled in this course to join its live class"}), 403

    return jsonify({
        "room_code": lc.room_code,
        "title": lc.title,
        "is_host": is_host,
        "status": lc.status,
    }), 200
