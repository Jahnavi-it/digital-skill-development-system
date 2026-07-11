from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Resume, User

resume_bp = Blueprint("resume", __name__)

DEFAULT_RESUME = {
    "full_name": "",
    "title": "",
    "email": "",
    "phone": "",
    "location": "",
    "summary": "",
    "education": [],   # [{degree, institution, year, score}]
    "skills": [],       # ["Python", "HTML/CSS", ...]
    "projects": [],     # [{name, description, tech, link}]
    "experience": [],   # [{role, company, duration, description}]
    "certifications": [],  # ["Course name - DSDS"]
    "links": {"github": "", "linkedin": "", "portfolio": ""},
}


@resume_bp.route("", methods=["GET"])
@jwt_required()
def get_resume():
    user_id = get_jwt_identity()
    resume = Resume.query.filter_by(user_id=user_id).first()
    if not resume:
        user = User.query.get(user_id)
        prefill = dict(DEFAULT_RESUME)
        if user:
            prefill["full_name"] = user.name
            prefill["email"] = user.email
            prefill["phone"] = user.phone or ""
        return jsonify({"resume": prefill, "is_new": True}), 200
    return jsonify({"resume": resume.data, "is_new": False, "updated_at": resume.updated_at.isoformat()}), 200


@resume_bp.route("", methods=["PUT"])
@jwt_required()
def save_resume():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    payload = dict(DEFAULT_RESUME)
    for key in payload:
        if key in data:
            payload[key] = data[key]

    resume = Resume.query.filter_by(user_id=user_id).first()
    if resume:
        resume.data = payload
    else:
        resume = Resume(user_id=user_id, data=payload)
        db.session.add(resume)
    db.session.commit()

    return jsonify({"message": "Resume saved", "resume": resume.data}), 200
