from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Assessment, Question, AssessmentAttempt, Course, User, PointsLog
from app.utils.gamification import check_and_award_badges

assessments_bp = Blueprint("assessments", __name__)


@assessments_bp.route("/course/<int:course_id>", methods=["GET"])
def list_for_course(course_id):
    assessments = Assessment.query.filter_by(course_id=course_id).all()
    return jsonify({"assessments": [
        {"id": a.id, "title": a.title, "total_marks": a.total_marks,
         "pass_marks": a.pass_marks, "question_count": len(a.questions)}
        for a in assessments
    ]}), 200


@assessments_bp.route("/<int:assessment_id>", methods=["GET"])
def get_assessment(assessment_id):
    """Returns questions WITHOUT the correct answer, so the quiz can be taken fairly."""
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return jsonify({"error": "Assessment not found"}), 404
    return jsonify({"assessment": assessment.to_dict(with_answers=False)}), 200


@assessments_bp.route("", methods=["POST"])
@jwt_required()
def create_assessment():
    """Mentors/admins create an assessment with its questions in one call."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role not in ("mentor", "admin"):
        return jsonify({"error": "Only mentors or admins can create assessments"}), 403

    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    title = (data.get("title") or "").strip()
    questions_data = data.get("questions", [])

    if not course_id or not title:
        return jsonify({"error": "course_id and title are required"}), 400
    if not Course.query.get(course_id):
        return jsonify({"error": "Course not found"}), 404
    if not questions_data:
        return jsonify({"error": "At least one question is required"}), 400

    assessment = Assessment(
        course_id=course_id, title=title,
        total_marks=data.get("total_marks", len(questions_data)),
        pass_marks=data.get("pass_marks", max(1, len(questions_data) // 2)),
    )
    db.session.add(assessment)
    db.session.flush()

    for q in questions_data:
        correct = (q.get("correct_option") or "").upper()
        if correct not in ("A", "B", "C", "D"):
            return jsonify({"error": "Each question needs a correct_option of A, B, C or D"}), 400
        db.session.add(Question(
            assessment_id=assessment.id,
            question_text=q.get("question_text", ""),
            option_a=q.get("option_a"), option_b=q.get("option_b"),
            option_c=q.get("option_c"), option_d=q.get("option_d"),
            correct_option=correct, marks=q.get("marks", 1),
        ))

    db.session.commit()
    return jsonify({"message": "Assessment created", "assessment": assessment.to_dict()}), 201


@assessments_bp.route("/<int:assessment_id>/submit", methods=["POST"])
@jwt_required()
def submit_assessment(assessment_id):
    """
    Body: { "answers": { "<question_id>": "A", "<question_id>": "C", ... } }
    Grades server-side against the correct_option stored in the DB.
    """
    user_id = get_jwt_identity()
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return jsonify({"error": "Assessment not found"}), 404

    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})

    score = 0
    results = []
    for question in assessment.questions:
        submitted = (answers.get(str(question.id)) or "").upper()
        is_correct = submitted == question.correct_option
        if is_correct:
            score += question.marks
        results.append({
            "question_id": question.id,
            "your_answer": submitted or None,
            "correct_option": question.correct_option,
            "is_correct": is_correct,
        })

    passed = score >= assessment.pass_marks

    attempt = AssessmentAttempt(user_id=user_id, assessment_id=assessment_id, score=score, passed=passed)
    db.session.add(attempt)

    user = User.query.get(user_id)
    awarded_points = 0
    if passed:
        awarded_points = 20
        db.session.add(PointsLog(user_id=user_id, points=awarded_points, reason=f"Passed assessment: {assessment.title}"))
        user.points = (user.points or 0) + awarded_points
        user.level = 1 + (user.points // 100)

    db.session.commit()
    new_badges = check_and_award_badges(user)

    return jsonify({
        "message": "Assessment submitted",
        "score": score,
        "total_marks": assessment.total_marks,
        "pass_marks": assessment.pass_marks,
        "passed": passed,
        "points_awarded": awarded_points,
        "results": results,
        "new_badges": [b.to_dict() for b in new_badges],
    }), 200


@assessments_bp.route("/my-attempts", methods=["GET"])
@jwt_required()
def my_attempts():
    user_id = get_jwt_identity()
    attempts = (
        AssessmentAttempt.query.filter_by(user_id=user_id)
        .order_by(AssessmentAttempt.attempted_at.desc())
        .all()
    )
    return jsonify({"attempts": [
        {
            "id": a.id, "assessment_id": a.assessment_id,
            "assessment_title": a.assessment.title if a.assessment else None,
            "score": a.score, "passed": a.passed,
            "attempted_at": a.attempted_at.isoformat(),
        } for a in attempts
    ]}), 200
