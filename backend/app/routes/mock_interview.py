import random
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import MockInterview
from app.data_bank import QUESTION_BANK, score_answer

mock_interview_bp = Blueprint("mock_interview", __name__)


@mock_interview_bp.route("/roles", methods=["GET"])
def roles():
    return jsonify({"roles": list(QUESTION_BANK.keys())}), 200


@mock_interview_bp.route("/questions", methods=["GET"])
def questions():
    role = request.args.get("role")
    if role not in QUESTION_BANK:
        return jsonify({"error": "Unknown role. Check /roles for valid options."}), 400
    bank = QUESTION_BANK[role]
    picked = random.sample(bank, k=min(5, len(bank)))
    # don't leak keywords to the client before they answer
    return jsonify({
        "role": role,
        "questions": [{"id": i, "q": item["q"]} for i, item in enumerate(picked)],
        "_internal": None,
    }), 200, {"X-Note": "keywords withheld until submit"}


def _questions_with_keywords(role):
    return QUESTION_BANK.get(role, [])


@mock_interview_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    answers = data.get("answers")  # [{q: "...", answer: "..."}]

    if role not in QUESTION_BANK or not isinstance(answers, list) or not answers:
        return jsonify({"error": "role and a non-empty answers list are required"}), 400

    bank_by_q = {item["q"]: item["keywords"] for item in QUESTION_BANK[role]}

    results = []
    total = 0
    for item in answers:
        q_text = item.get("q", "")
        ans_text = item.get("answer", "")
        keywords = bank_by_q.get(q_text, [])
        pct = score_answer(ans_text, keywords)
        total += pct
        results.append({"q": q_text, "answer": ans_text, "score_percent": pct})

    overall = round(total / len(results)) if results else 0

    record = MockInterview(
        user_id=user_id,
        role_applied=role,
        questions=[r["q"] for r in results],
        answers=[r["answer"] for r in results],
        score=overall,
    )
    db.session.add(record)
    db.session.commit()

    feedback = (
        "Strong answers — you're covering the key concepts well." if overall >= 70 else
        "Decent attempt, but try to mention more of the core technical terms." if overall >= 40 else
        "Review the fundamentals for this role before your next attempt."
    )

    return jsonify({
        "message": "Interview submitted",
        "id": record.id,
        "overall_score": overall,
        "feedback": feedback,
        "results": results,
    }), 201


@mock_interview_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    records = MockInterview.query.filter_by(user_id=user_id).order_by(MockInterview.created_at.desc()).all()
    return jsonify({"history": [
        {
            "id": r.id,
            "role_applied": r.role_applied,
            "score": r.score,
            "created_at": r.created_at.isoformat(),
        } for r in records
    ]}), 200
