"""Run after seed_demo.py: python seed_phase3.py"""
from app import create_app, db
from app.models import Internship

app = create_app()

SAMPLE_INTERNSHIPS = [
    dict(title="Frontend Developer Intern", company="Brightwave Tech",
         description="Work on responsive UI components using HTML, CSS and JavaScript.",
         skills_required="Web Development, HTML, CSS, JavaScript", apply_link="https://example.com/apply/1"),
    dict(title="Python Backend Intern", company="Codeforge Labs",
         description="Build REST APIs and help maintain internal tools using Python/Flask.",
         skills_required="Programming, Python, Flask", apply_link="https://example.com/apply/2"),
    dict(title="Data Analyst Intern", company="Insightly Analytics",
         description="Clean datasets and build dashboards to support business decisions.",
         skills_required="Data Science, Python, SQL", apply_link="https://example.com/apply/3"),
    dict(title="Digital Marketing Intern", company="Reach Media Co.",
         description="Assist with SEO, social media campaigns and content scheduling.",
         skills_required="Digital Marketing, SEO, Content Writing", apply_link="https://example.com/apply/4"),
    dict(title="IT Support Intern", company="NextGen Solutions",
         description="Help with basic troubleshooting, system setup and documentation.",
         skills_required="Basic Computer Skills, Networking", apply_link="https://example.com/apply/5"),
    dict(title="Full Stack Intern", company="Skyline Softworks",
         description="Contribute to both frontend and backend of a customer-facing product.",
         skills_required="Web Development, Programming, JavaScript, Python", apply_link="https://example.com/apply/6"),
]

with app.app_context():
    for item in SAMPLE_INTERNSHIPS:
        if not Internship.query.filter_by(title=item["title"], company=item["company"]).first():
            db.session.add(Internship(**item))
    db.session.commit()
    print(f"Seeded {len(SAMPLE_INTERNSHIPS)} internships (skipping duplicates).")
