"""
Coding Compiler — runs user-submitted code via `subprocess` with a timeout,
so students can practice on the platform without needing a local IDE.
Academic-project note: this uses process-level isolation (timeout + temp file
+ resource limits on Linux) which is enough for a CSP demo. It is NOT a
production-grade sandbox — a real deployment would run each submission
inside a locked-down Docker/gVisor container with no network access.
"""
import os
import subprocess
import sys
import tempfile
import platform

try:
    import resource  # Unix/Linux only — not available on Windows
except ImportError:
    resource = None

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CodingSubmission
coding_bp = Blueprint("coding", __name__)
TIMEOUT_SECONDS = 5
MAX_OUTPUT_CHARS = 4000
MAX_MEMORY_MB = 128
RUNNERS = {
    "python": {"ext": ".py", "cmd": lambda path: [sys.executable, path]},
    "javascript": {"ext": ".js", "cmd": lambda path: ["node", path]},
}
def _limit_resources():
    """Runs in the child process (Linux only) right before exec to cap memory/CPU."""
    if platform.system() != "Linux" or resource is None:
        return
    mem_bytes = MAX_MEMORY_MB * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_SECONDS, TIMEOUT_SECONDS))
def run_code(language, code, stdin_data):
    runner = RUNNERS.get(language)
    if not runner:
        return None, f"Unsupported language '{language}'. Supported: {', '.join(RUNNERS)}", "error"
    with tempfile.NamedTemporaryFile(mode="w", suffix=runner["ext"], delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        preexec = _limit_resources if platform.system() == "Linux" else None
        proc = subprocess.run(
            runner["cmd"](tmp_path),
            input=stdin_data or "",
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            preexec_fn=preexec,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        status = "success" if proc.returncode == 0 else "error"
        return output[:MAX_OUTPUT_CHARS], None, status
    except subprocess.TimeoutExpired:
        return None, "Execution timed out (5s limit). Check for infinite loops.", "timeout"
    except FileNotFoundError:
        return None, f"'{language}' runtime is not installed on this server.", "error"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
@coding_bp.route("/languages", methods=["GET"])
def languages():
    return jsonify({"languages": list(RUNNERS.keys())}), 200
@coding_bp.route("/run", methods=["POST"])
@jwt_required()
def run():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    language = (data.get("language") or "").lower()
    code = data.get("code") or ""
    stdin_data = data.get("stdin") or ""
    if not code.strip():
        return jsonify({"error": "code is required"}), 400
    output, err, status = run_code(language, code, stdin_data)
    submission = CodingSubmission(
        user_id=user_id, language=language, code=code, stdin_data=stdin_data,
        output=output or err, status=status,
    )
    db.session.add(submission)
    db.session.commit()
    if err and status == "error" and output is None:
        return jsonify({"error": err, "status": status, "submission_id": submission.id}), 400
    return jsonify({"output": output, "status": status, "submission_id": submission.id}), 200
@coding_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    subs = CodingSubmission.query.filter_by(user_id=user_id).order_by(CodingSubmission.submitted_at.desc()).limit(20).all()
    return jsonify({"history": [
        {
            "id": s.id, "language": s.language, "status": s.status,
            "submitted_at": s.submitted_at.isoformat(),
        } for s in subs
    ]}), 200