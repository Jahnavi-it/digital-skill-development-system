from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Course, Category, Lesson, Enrollment, LessonProgress, User, PointsLog
from app.utils.gamification import check_and_award_badges

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify({"categories": [c.to_dict() for c in categories]}), 200


@courses_bp.route("", methods=["GET"])
def list_courses():
    category_id = request.args.get("category_id", type=int)
    level = request.args.get("level")
    search = request.args.get("search", "").strip()

    query = Course.query.filter_by(is_published=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if level:
        query = query.filter_by(level=level)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))

    courses = query.order_by(Course.created_at.desc()).all()
    return jsonify({"courses": [c.to_dict() for c in courses]}), 200


@courses_bp.route("/<int:course_id>", methods=["GET"])
def course_detail(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify({"course": course.to_dict(include_lessons=True)}), 200


@courses_bp.route("", methods=["POST"])
@jwt_required()
def create_course():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in ("mentor", "admin"):
        return jsonify({"error": "Only mentors or admins can create courses"}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    category_id = data.get("category_id")
    if not title or not category_id:
        return jsonify({"error": "title and category_id are required"}), 400

    course = Course(
        title=title,
        description=data.get("description", ""),
        category_id=category_id,
        mentor_id=user.id,
        level=data.get("level", "beginner"),
        thumbnail_url=data.get("thumbnail_url"),
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Course created", "course": course.to_dict()}), 201


@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@jwt_required()
def enroll_course(course_id):
    user_id = get_jwt_identity()
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return jsonify({"message": "Already enrolled", "enrollment": existing.to_dict()}), 200

    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrolled successfully", "enrollment": enrollment.to_dict()}), 201


@courses_bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
@jwt_required()
def complete_lesson(lesson_id):
    user_id = get_jwt_identity()
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    already_done = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not already_done:
        db.session.add(LessonProgress(user_id=user_id, lesson_id=lesson_id))
        db.session.add(PointsLog(user_id=user_id, points=5, reason=f"Completed lesson: {lesson.title}"))
        user = User.query.get(user_id)
        user.points = (user.points or 0) + 5
        user.level = 1 + (user.points // 100)

    # Recalculate progress percentage for this course
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=lesson.course_id).first()
    if enrollment:
        total_lessons = Lesson.query.filter_by(course_id=lesson.course_id).count()
        completed = (
            db.session.query(LessonProgress)
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .filter(LessonProgress.user_id == user_id, Lesson.course_id == lesson.course_id)
            .count()
        )
        enrollment.progress_percent = round((completed / total_lessons) * 100, 2) if total_lessons else 0
        if enrollment.progress_percent >= 100:
            enrollment.status = "completed"

    db.session.commit()

    user = User.query.get(user_id)
    new_badges = check_and_award_badges(user)

    return jsonify({
        "message": "Lesson marked complete",
        "new_badges": [b.to_dict() for b in new_badges],
    }), 200
