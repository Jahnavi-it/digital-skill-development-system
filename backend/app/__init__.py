from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    socketio.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.assessments import assessments_bp
    from app.routes.resume import resume_bp
    from app.routes.mock_interview import mock_interview_bp
    from app.routes.coding import coding_bp
    from app.routes.internships import internships_bp
    from app.routes.forum import forum_bp
    from app.routes.notifications import notifications_bp
    from app.routes.chat import chat_bp
    from app.routes.live_classes import live_classes_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(assessments_bp, url_prefix="/api/assessments")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(mock_interview_bp, url_prefix="/api/mock-interview")
    app.register_blueprint(coding_bp, url_prefix="/api/coding")
    app.register_blueprint(internships_bp, url_prefix="/api/internships")
    app.register_blueprint(forum_bp, url_prefix="/api/forum")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(live_classes_bp, url_prefix="/api/live-classes")

    from app import sockets

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Digital Skill Development System API running"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app