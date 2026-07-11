from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Enrollment, UserBadge, Badge

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    top_users = (
        User.query.filter_by(role="student")
        .order_by(User.points.desc())
        .limit(10)
        .all()
    )
    return jsonify({"leaderboard": [
        {"rank": i + 1, "name": u.name, "points": u.points, "level": u.level}
        for i, u in enumerate(top_users)
    ]}), 200


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def dashboard_summary():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    badges = (
        UserBadge.query.filter_by(user_id=user_id)
        .join(Badge, Badge.id == UserBadge.badge_id)
        .with_entities(Badge)
        .all()
    )

    active = [e.to_dict() for e in enrollments if e.status == "active"]
    completed = [e.to_dict() for e in enrollments if e.status == "completed"]

    # Points needed to reach the next level (100 points per level)
    points_to_next_level = 100 - (user.points % 100)

    return jsonify({
        "user": user.to_dict(),
        "stats": {
            "courses_enrolled": len(enrollments),
            "courses_completed": len(completed),
            "courses_in_progress": len(active),
            "points": user.points,
            "level": user.level,
            "points_to_next_level": points_to_next_level,
        },
        "active_courses": active,
        "completed_courses": completed,
        "badges": [b.to_dict() for b in badges],
    }), 200
