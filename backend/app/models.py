from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("student", "mentor", "admin", name="role_enum"), default="student")
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(255))
    language_pref = db.Column(db.Enum("en", "te", "hi", name="lang_enum"), default="en")
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "language_pref": self.language_pref,
            "points": self.points,
            "level": self.level,
        }


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "icon": self.icon}


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.Enum("beginner", "intermediate", "advanced", name="course_level_enum"), default="beginner")
    thumbnail_url = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lessons = db.relationship("Lesson", backref="course", cascade="all, delete-orphan")
    category = db.relationship("Category")

    def to_dict(self, include_lessons=False):
        data = {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "mentor_id": self.mentor_id,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "thumbnail_url": self.thumbnail_url,
            "lesson_count": len(self.lessons),
        }
        if include_lessons:
            data["lessons"] = [l.to_dict() for l in sorted(self.lessons, key=lambda x: x.sequence_no)]
        return data


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content_type = db.Column(db.Enum("video", "text", "quiz", name="content_type_enum"), default="text")
    content_url = db.Column(db.String(255))
    content_text = db.Column(db.Text)
    sequence_no = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "content_type": self.content_type,
            "content_url": self.content_url,
            "content_text": self.content_text,
            "sequence_no": self.sequence_no,
        }


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    progress_percent = db.Column(db.Numeric(5, 2), default=0)
    status = db.Column(db.Enum("active", "completed", "dropped", name="enrollment_status_enum"), default="active")
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship("Course")

    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="uniq_enrollment"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "course_title": self.course.title if self.course else None,
            "progress_percent": float(self.progress_percent),
            "status": self.status,
            "enrolled_at": self.enrolled_at.isoformat(),
        }


class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uniq_lesson_progress"),)


class Assessment(db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    total_marks = db.Column(db.Integer, default=100)
    pass_marks = db.Column(db.Integer, default=40)

    questions = db.relationship("Question", backref="assessment", cascade="all, delete-orphan")

    def to_dict(self, with_answers=False):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "total_marks": self.total_marks,
            "pass_marks": self.pass_marks,
            "questions": [q.to_dict(with_answers) for q in self.questions],
        }


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.Enum("A", "B", "C", "D", name="correct_option_enum"), nullable=False)
    marks = db.Column(db.Integer, default=1)

    def to_dict(self, with_answer=False):
        data = {
            "id": self.id,
            "question_text": self.question_text,
            "option_a": self.option_a,
            "option_b": self.option_b,
            "option_c": self.option_c,
            "option_d": self.option_d,
            "marks": self.marks,
        }
        if with_answer:
            data["correct_option"] = self.correct_option
        return data


class AssessmentAttempt(db.Model):
    __tablename__ = "assessment_attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    score = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    assessment = db.relationship("Assessment")


class Badge(db.Model):
    __tablename__ = "badges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    points_required = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "icon": self.icon, "points_required": self.points_required,
        }


class UserBadge(db.Model):
    __tablename__ = "user_badges"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)


class PointsLog(db.Model):
    __tablename__ = "points_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---- Models below are defined now so later phases can build on them directly ----

class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MockInterview(db.Model):
    __tablename__ = "mock_interviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_applied = db.Column(db.String(120))
    questions = db.Column(db.JSON)
    answers = db.Column(db.JSON)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CodingSubmission(db.Model):
    __tablename__ = "coding_submissions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    language = db.Column(db.String(30))
    code = db.Column(db.Text)
    stdin_data = db.Column(db.Text)
    output = db.Column(db.Text)
    status = db.Column(db.String(30))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Internship(db.Model):
    __tablename__ = "internships"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    description = db.Column(db.Text)
    skills_required = db.Column(db.String(255))
    apply_link = db.Column(db.String(255))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)


class ForumThread(db.Model):
    __tablename__ = "forum_threads"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    category = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ForumReply(db.Model):
    __tablename__ = "forum_replies"
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("forum_threads.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class LiveClass(db.Model):
    __tablename__ = "live_classes"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150))
    scheduled_at = db.Column(db.DateTime)
    room_code = db.Column(db.String(50))
    status = db.Column(db.Enum("scheduled", "live", "ended", name="live_status_enum"), default="scheduled")

    course = db.relationship("Course")
    mentor = db.relationship("User")
