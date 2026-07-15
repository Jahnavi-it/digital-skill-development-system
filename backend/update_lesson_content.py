"""
Updates existing Lesson rows with real written content and a YouTube intro
video for the first lesson of each course. Safe to run multiple times.

Usage:  python update_lesson_content.py

Reads the same DB connection your app already uses (.env DATABASE_URL or
DB_* values), so run this against whichever database your backend is
currently pointed at.
"""
from app import create_app, db
from app.models import Course, Lesson

app = create_app()

# course_title -> { lesson_title: {content_text, content_type?, content_url?} }
LESSON_CONTENT = {
    "HTML & CSS Foundations": {
        "Introduction to HTML": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/916GWv2Qs08",
            "content_text": (
                "HTML (HyperText Markup Language) is the standard language used to structure content on "
                "the web. Every web page is built from HTML elements — tags like <h1>, <p>, and <img> — "
                "that tell the browser what each piece of content is (a heading, a paragraph, an image, "
                "and so on). In this lesson you'll set up a basic HTML file, learn the standard document "
                "structure (<!DOCTYPE html>, <html>, <head>, <body>), and create your first web page with "
                "headings, paragraphs, links, and images. Watch the video above for a hands-on walkthrough."
            ),
        },
        "Structuring a Web Page": {
            "content_text": (
                "A well-structured web page uses semantic HTML elements — tags that describe their meaning, "
                "not just their appearance. Instead of wrapping everything in generic <div> tags, use "
                "<header> for the top of the page, <nav> for navigation links, <main> for primary content, "
                "<section> and <article> to group related content, and <footer> for the bottom. Semantic "
                "HTML makes your page easier to read, more accessible to screen readers, and better for "
                "SEO because search engines can understand your content's structure."
            ),
        },
        "Styling with CSS": {
            "content_text": (
                "CSS (Cascading Style Sheets) controls how HTML elements look — colors, fonts, spacing, and "
                "layout. You can attach CSS to a page three ways: inline (style=\"...\" on a tag), internal "
                "(a <style> block in <head>), or external (a separate .css file linked with <link>) — "
                "external is the standard for real projects. CSS selectors target elements by tag, class "
                "(.my-class), or id (#my-id), and every element follows the 'box model': content, padding, "
                "border, and margin, from the inside out. Practice by styling text color, background, and "
                "spacing on the page you built in the previous lesson."
            ),
        },
        "Responsive Layouts with Flexbox": {
            "content_text": (
                "Flexbox is a CSS layout system designed for arranging items in a single row or column that "
                "can grow, shrink, and wrap based on screen size — perfect for responsive design. Setting "
                "display: flex on a container turns its children into flex items you can align and space "
                "using properties like justify-content (horizontal alignment) and align-items (vertical "
                "alignment). Combine Flexbox with media queries (@media (max-width: 768px) { ... }) to "
                "change layouts on smaller screens, so your page looks good on both desktop and mobile."
            ),
        },
    },
    "JavaScript Essentials": {
        "Variables & Data Types": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/hdI2bqOjy3c",
            "content_text": (
                "JavaScript is the programming language that makes web pages interactive. Variables store "
                "data using let (can be reassigned) or const (cannot be reassigned) — avoid the older 'var'. "
                "JavaScript's core data types are strings (text), numbers, booleans (true/false), arrays "
                "(ordered lists), objects (key-value pairs), null, and undefined. Because JavaScript is "
                "dynamically typed, a variable's type is decided by the value you give it, and can change "
                "later in the program. Watch the video above to see these in action."
            ),
        },
        "Functions & Scope": {
            "content_text": (
                "A function is a reusable block of code you define once and call whenever you need it — "
                "for example function greet(name) { return `Hello, ${name}`; }. JavaScript also supports a "
                "shorter arrow function syntax: const greet = (name) => `Hello, ${name}`. Scope determines "
                "where a variable is accessible: variables declared with let/const inside a function or "
                "block ({ }) only exist inside that block, while variables declared outside any function "
                "are globally accessible. Understanding scope helps you avoid bugs where a variable is "
                "accidentally overwritten or unavailable where you expect it."
            ),
        },
        "DOM Manipulation": {
            "content_text": (
                "The DOM (Document Object Model) is the browser's live representation of your HTML page as "
                "a tree of objects that JavaScript can read and change. Common methods include "
                "document.querySelector('.class') to find an element, .textContent or .innerHTML to change "
                "its content, .style to change its CSS, and .addEventListener('click', fn) to respond to "
                "user actions like clicks. This is how JavaScript makes pages interactive — showing/hiding "
                "menus, validating forms, updating a counter, and much more, all without reloading the page."
            ),
        },
        "Working with APIs": {
            "content_text": (
                "An API (Application Programming Interface) lets your JavaScript code request data from a "
                "server — for example, fetching weather data or a list of products. The modern fetch() "
                "function sends a request and returns a Promise: fetch('https://api.example.com/data')"
                ".then(res => res.json()).then(data => console.log(data)). Many developers prefer "
                "async/await syntax for readability: const res = await fetch(url); const data = await "
                "res.json(). Working with APIs is essential for building dynamic sites that show real, "
                "up-to-date information instead of static content."
            ),
        },
    },
    "Python for Beginners": {
        "Setting up Python": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/W4D50QimIZQ",
            "content_text": (
                "Python is a beginner-friendly, general-purpose programming language used in web "
                "development, data science, automation, and more. To get started, install Python from "
                "python.org (or use an online editor like Replit while you're learning), then write your "
                "first program: print(\"Hello, World!\"). Python code runs top-to-bottom, uses indentation "
                "(not curly braces) to define blocks of code, and doesn't require semicolons at the end of "
                "lines. Watch the video above for a full walkthrough of installation and your first script."
            ),
        },
        "Variables & Loops": {
            "content_text": (
                "In Python, you create a variable simply by assigning a value: name = \"Ramana\", age = 21. "
                "Python figures out the type automatically (string, integer, float, boolean). Loops let you "
                "repeat code: a for loop iterates over a sequence (for i in range(5): print(i)), while a "
                "while loop repeats as long as a condition is true (while count < 10: ...). Loops are "
                "essential for processing lists of data, repeating tasks, and building interactive programs "
                "like guessing games or menus."
            ),
        },
        "Functions": {
            "content_text": (
                "A Python function is defined with the def keyword: def add(a, b): return a + b. Functions "
                "let you package logic into a reusable, named block instead of repeating code everywhere. "
                "You can give parameters default values (def greet(name=\"friend\"):), and use keyword "
                "arguments when calling a function for clarity (greet(name=\"Ramana\")). Writing small, "
                "focused functions makes your programs easier to read, test, and debug."
            ),
        },
        "Lists & Dictionaries": {
            "content_text": (
                "Lists store an ordered collection of items: fruits = [\"apple\", \"banana\", \"mango\"], "
                "accessed by index (fruits[0]) and modified with methods like .append() and .remove(). "
                "Dictionaries store key-value pairs: student = {\"name\": \"Ramana\", \"age\": 21}, accessed "
                "by key (student[\"name\"]) rather than position. Lists are best when order matters (a "
                "sequence of steps, a queue); dictionaries are best when you need to look things up by a "
                "meaningful label. Both are fundamental to almost every real Python program."
            ),
        },
    },
    "SEO Basics": {
        "How Search Engines Work": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/xsVTqzratPs",
            "content_text": (
                "Search engines like Google use automated programs called crawlers (or 'bots') to discover "
                "and read pages across the web, following links from page to page. Discovered pages are "
                "added to a massive index — essentially a giant database of web content. When someone "
                "searches, the engine's ranking algorithm scores indexed pages against the query using "
                "hundreds of signals (relevance, content quality, site speed, backlinks, mobile-friendliness) "
                "and returns the best matches in order. SEO is the practice of optimizing your site so "
                "search engines can crawl it easily and rank it well for relevant searches."
            ),
        },
        "Keyword Research": {
            "content_text": (
                "Keyword research is finding the exact words and phrases your target audience types into "
                "search engines, so you can create content that matches their intent. Start by brainstorming "
                "topics related to your business, then use tools (Google Keyword Planner, Ubersuggest, or "
                "even Google's autocomplete/related searches) to find search volume and related terms. "
                "Prioritize keywords with a good balance of decent search volume and realistic competition "
                "— for a new site, long-tail keywords (longer, more specific phrases like 'best budget "
                "laptop for students' rather than just 'laptop') are usually easier to rank for."
            ),
        },
        "On-Page SEO": {
            "content_text": (
                "On-page SEO means optimizing the content and HTML of a specific page so it ranks well for "
                "its target keyword. Key elements include: a clear, keyword-relevant <title> tag, a "
                "compelling meta description, one <h1> that matches the page's main topic, well-organized "
                "subheadings (<h2>, <h3>), naturally-placed keywords in the body text, descriptive alt text "
                "on images, and internal links to related pages on your site. The goal is always to write "
                "genuinely useful content for readers first — good on-page SEO makes that content easier "
                "for search engines to understand, not the other way around."
            ),
        },
        "Building Backlinks": {
            "content_text": (
                "A backlink is a link from another website pointing to yours — search engines treat these "
                "as a vote of confidence, especially from reputable, relevant sites. Ways to earn backlinks "
                "include creating genuinely useful content that others want to reference (guides, original "
                "research, tools), guest posting on relevant blogs, getting listed in industry directories, "
                "and building relationships with other site owners in your niche. Avoid buying links or "
                "using link farms — search engines penalize manipulative link schemes, and a few "
                "high-quality backlinks are worth far more than many low-quality ones."
            ),
        },
    },
    "Intro to Data Analysis": {
        "What is Data Science": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/r-uOLxNrNk8",
            "content_text": (
                "Data science is the process of collecting, cleaning, analyzing, and interpreting data to "
                "answer questions and support decisions — used in business, healthcare, sports, government, "
                "and almost every other field. A typical workflow: define the question, gather the relevant "
                "data, clean it (handle missing or incorrect values), explore it with statistics and charts, "
                "then draw conclusions or build a predictive model. This course focuses on the foundational "
                "skills — spreadsheets, basic statistics, and visualization — that every data analysis "
                "workflow builds on."
            ),
        },
        "Working with Spreadsheets": {
            "content_text": (
                "Spreadsheets (Excel or Google Sheets) are often the fastest way to explore small-to-medium "
                "datasets. Key skills: sorting and filtering rows to focus on relevant data, using formulas "
                "(SUM, AVERAGE, COUNTIF) to summarize data, VLOOKUP/XLOOKUP to pull matching data from "
                "another table, and pivot tables to summarize large datasets by category (e.g. total sales "
                "per region per month) without writing any code. Getting comfortable with spreadsheets is a "
                "great foundation before moving on to programming-based analysis with Python or SQL."
            ),
        },
        "Intro to Statistics": {
            "content_text": (
                "Basic statistics help you describe and interpret data. Measures of central tendency — mean "
                "(average), median (middle value), and mode (most frequent value) — summarize where your "
                "data is centered, while measures of spread like range and standard deviation show how "
                "varied the data is. Understanding the difference between correlation (two things moving "
                "together) and causation (one thing causing another) is one of the most important skills in "
                "data analysis — just because two variables are related doesn't mean one causes the other."
            ),
        },
        "Data Visualization Basics": {
            "content_text": (
                "Visualizing data turns rows of numbers into charts that are far easier for people to "
                "understand at a glance. Use bar charts to compare categories, line charts to show trends "
                "over time, pie charts sparingly for simple part-to-whole comparisons, and scatter plots to "
                "reveal relationships between two numeric variables. Good visualizations have a clear title, "
                "labeled axes, and avoid unnecessary decoration ('chart junk') that distracts from the data "
                "— the goal is always to make the underlying pattern as easy to see as possible."
            ),
        },
    },
    "Computer Fundamentals": {
        "Parts of a Computer": {
            "content_type": "video",
            "content_url": "https://www.youtube.com/embed/y2kg3MOk1sY",
            "content_text": (
                "Every computer has core hardware components working together: the CPU (Central Processing "
                "Unit) executes instructions and is often called the 'brain' of the computer; RAM (memory) "
                "temporarily holds data the CPU is actively using and is cleared when you power off; storage "
                "(an SSD or hard drive) permanently holds your files and programs; and input/output devices "
                "(keyboard, mouse, monitor) let you interact with the system. Understanding these basics "
                "helps you troubleshoot problems and make sense of specs when buying a device."
            ),
        },
        "Operating System Basics": {
            "content_text": (
                "The operating system (OS) — Windows, macOS, or Linux — is the software that manages a "
                "computer's hardware and runs all other programs. It handles tasks like allocating memory to "
                "apps, managing files, connecting to networks and printers, and providing the graphical "
                "interface (desktop, icons, taskbar/dock) you interact with. Learning your OS's basics — "
                "opening/closing apps, using the file explorer, adjusting settings, and installing software "
                "safely — is the foundation for using a computer confidently and productively."
            ),
        },
        "File Management": {
            "content_text": (
                "Good file management means organizing your files into a clear folder structure (e.g. "
                "Documents > Projects > ProjectName) instead of leaving everything on the desktop. Use "
                "descriptive file names with dates or version numbers when relevant (report_2026_final.docx), "
                "regularly back up important files (cloud storage or an external drive), and periodically "
                "delete files you no longer need. Being able to quickly find, rename, move, copy, and delete "
                "files is a foundational digital skill that saves enormous time in school and work."
            ),
        },
        "Using the Internet Safely": {
            "content_text": (
                "Staying safe online starts with strong, unique passwords for each account (a password "
                "manager helps) and enabling two-factor authentication wherever it's offered. Be cautious of "
                "phishing — emails or messages that pretend to be from a trusted source to trick you into "
                "clicking a malicious link or sharing personal information; always check the sender's actual "
                "email address and hover over links before clicking. Keep your browser and OS updated (updates "
                "often patch security holes), avoid downloading software from untrusted sites, and think "
                "twice before sharing personal information publicly on social media."
            ),
        },
    },
}


with app.app_context():
    updated = 0
    skipped = 0
    for course_title, lessons in LESSON_CONTENT.items():
        course = Course.query.filter_by(title=course_title).first()
        if not course:
            print(f"Course '{course_title}' not found — skipping.")
            continue
        for lesson_title, content in lessons.items():
            lesson = Lesson.query.filter_by(course_id=course.id, title=lesson_title).first()
            if not lesson:
                print(f"Lesson '{lesson_title}' not found under '{course_title}' — skipping.")
                skipped += 1
                continue
            lesson.content_text = content["content_text"]
            if "content_type" in content:
                lesson.content_type = content["content_type"]
            if "content_url" in content:
                lesson.content_url = content["content_url"]
            updated += 1
            print(f"Updated: {course_title} > {lesson_title}")

    db.session.commit()
    print(f"\nDone. Updated {updated} lessons, skipped {skipped}.")
