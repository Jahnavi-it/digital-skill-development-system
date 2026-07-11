"""
Badge-awarding rules.

Each badge in the `badges` table has a specific, hardcoded condition here.
This keeps gamification logic in one place so new badges are added by:
  1. inserting a row into `badges`
  2. adding one `if` block below
"""
from app import db
from app.models import Badge, UserBadge, Enrollment, LessonProgress, AssessmentAttempt, Notification


def _already_has(user_id, badge_name):
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        return True  # badge not seeded, nothing to award
    return UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first() is not None


def _award(user_id, badge_name):
    if _already_has(user_id, badge_name):
        return None
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        return None
    db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
    db.session.add(Notification(user_id=user_id, message=f"You earned the '{badge.name}' badge!"))
    return badge


def check_and_award_badges(user):
    """Call this after points/progress changes. Returns list of newly earned Badge objects."""
    newly_earned = []

    lessons_done = LessonProgress.query.filter_by(user_id=user.id).count()
    if lessons_done >= 1:
        b = _award(user.id, "First Step")
        if b: newly_earned.append(b)

    courses_completed = Enrollment.query.filter_by(user_id=user.id, status="completed").count()
    if courses_completed >= 1:
        b = _award(user.id, "Course Champion")
        if b: newly_earned.append(b)

    quizzes_passed = AssessmentAttempt.query.filter_by(user_id=user.id, passed=True).count()
    if quizzes_passed >= 5:
        b = _award(user.id, "Quiz Master")
        if b: newly_earned.append(b)

    if user.level >= 5:
        b = _award(user.id, "Rising Star")
        if b: newly_earned.append(b)

    if newly_earned:
        db.session.commit()
    return newly_earned
