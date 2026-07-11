from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Internship, Enrollment, Course, User

internships_bp = Blueprint("internships", __name__)


def _to_dict(i):
    return {
        "id": i.id, "title": i.title, "company": i.company, "description": i.description,
        "skills_required": [s.strip() for s in (i.skills_required or "").split(",") if s.strip()],
        "apply_link": i.apply_link, "posted_at": i.posted_at.isoformat(),
    }


@internships_bp.route("", methods=["GET"])
def list_internships():
    skill = request.args.get("skill")
    query = Internship.query
    if skill:
        query = query.filter(Internship.skills_required.ilike(f"%{skill}%"))
    items = query.order_by(Internship.posted_at.desc()).all()
    return jsonify({"internships": [_to_dict(i) for i in items]}), 200


@internships_bp.route("/recommended", methods=["GET"])
@jwt_required()
def recommended():
    """
    Rule-based matching (no AI): builds the learner's skill set from the
    category names of courses they're enrolled in / completed, then ranks
    open internships by how many required skills overlap.
    """
    user_id = get_jwt_identity()
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    user_skills = set()
    for e in enrollments:
        if e.course and e.course.category:
            user_skills.add(e.course.category.name.lower())
        if e.course:
            user_skills.add(e.course.title.lower())

    internships = Internship.query.order_by(Internship.posted_at.desc()).all()
    scored = []
    for i in internships:
        req_skills = {s.strip().lower() for s in (i.skills_required or "").split(",") if s.strip()}
        overlap = sum(1 for rs in req_skills for us in user_skills if rs in us or us in rs)
        scored.append((overlap, i))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [s for s in scored if s[0] > 0][:10] or [s for s in scored[:5]]

    return jsonify({
        "matched_on_skills": sorted(user_skills),
        "internships": [{**_to_dict(i), "match_score": score} for score, i in top],
    }), 200
