"""
Run this once after creating the database and tables to add demo courses.
Usage:  python seed_demo.py
"""
from app import create_app, db
from app.models import Category, Course, Lesson, Assessment, Question

app = create_app()

SAMPLE_QUIZ = {
    "course_title": "HTML & CSS Foundations",
    "quiz_title": "HTML & CSS Basics Quiz",
    "questions": [
        {"question_text": "Which tag is used to create a hyperlink in HTML?",
         "option_a": "<link>", "option_b": "<a>", "option_c": "<href>", "option_d": "<url>",
         "correct_option": "B"},
        {"question_text": "Which CSS property changes the text color?",
         "option_a": "font-color", "option_b": "text-color", "option_c": "color", "option_d": "fg-color",
         "correct_option": "C"},
        {"question_text": "Which HTML tag is used for the largest heading?",
         "option_a": "<h6>", "option_b": "<heading>", "option_c": "<head>", "option_d": "<h1>",
         "correct_option": "D"},
        {"question_text": "Which CSS layout model uses 'justify-content' and 'align-items'?",
         "option_a": "Grid", "option_b": "Flexbox", "option_c": "Float", "option_d": "Table",
         "correct_option": "B"},
    ],
}

DEMO_COURSES = {
    "Web Development": [
        ("HTML & CSS Foundations", "beginner", [
            "Introduction to HTML", "Structuring a Web Page", "Styling with CSS", "Responsive Layouts with Flexbox",
        ]),
        ("JavaScript Essentials", "intermediate", [
            "Variables & Data Types", "Functions & Scope", "DOM Manipulation", "Working with APIs",
        ]),
    ],
    "Programming": [
        ("Python for Beginners", "beginner", [
            "Setting up Python", "Variables & Loops", "Functions", "Lists & Dictionaries",
        ]),
    ],
    "Digital Marketing": [
        ("SEO Basics", "beginner", [
            "How Search Engines Work", "Keyword Research", "On-Page SEO", "Building Backlinks",
        ]),
    ],
    "Data Science": [
        ("Intro to Data Analysis", "beginner", [
            "What is Data Science", "Working with Spreadsheets", "Intro to Statistics", "Data Visualization Basics",
        ]),
    ],
    "Basic Computer Skills": [
        ("Computer Fundamentals", "beginner", [
            "Parts of a Computer", "Operating System Basics", "File Management", "Using the Internet Safely",
        ]),
    ],
}

with app.app_context():
    for cat_name, courses in DEMO_COURSES.items():
        category = Category.query.filter_by(name=cat_name).first()
        if not category:
            print(f"Category '{cat_name}' not found — run schema.sql first.")
            continue
        for title, level, lessons in courses:
            existing = Course.query.filter_by(title=title).first()
            if existing:
                continue
            course = Course(title=title, description=f"Learn {title} step by step.",
                             category_id=category.id, level=level)
            db.session.add(course)
            db.session.flush()  # get course.id before commit
            for i, lesson_title in enumerate(lessons, start=1):
                db.session.add(Lesson(
                    course_id=course.id, title=lesson_title,
                    content_type="text", sequence_no=i,
                    content_text=f"Content for '{lesson_title}' goes here.",
                ))
            print(f"Added course: {title}")
    # Seed one sample assessment so the quiz flow can be tested end-to-end
    quiz_course = Course.query.filter_by(title=SAMPLE_QUIZ["course_title"]).first()
    if quiz_course and not Assessment.query.filter_by(title=SAMPLE_QUIZ["quiz_title"]).first():
        assessment = Assessment(course_id=quiz_course.id, title=SAMPLE_QUIZ["quiz_title"],
                                 total_marks=len(SAMPLE_QUIZ["questions"]),
                                 pass_marks=max(1, len(SAMPLE_QUIZ["questions"]) // 2))
        db.session.add(assessment)
        db.session.flush()
        for q in SAMPLE_QUIZ["questions"]:
            db.session.add(Question(assessment_id=assessment.id, **q))
        print(f"Added sample assessment: {SAMPLE_QUIZ['quiz_title']}")

    db.session.commit()
    print("Demo data seeded successfully.")
