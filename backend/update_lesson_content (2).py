"""
Updates all seeded lessons with real, written content (instead of the
placeholder "Content for '...' goes here." text), and adds a YouTube
video embed to the first lesson of each course.

Usage (from the backend/ folder, with venv activated):
    python update_lesson_content.py
"""
from app import create_app, db
from app.models import Lesson, Course

app = create_app()

# course_title -> list of (lesson_title, content_text, optional video_url)
LESSON_CONTENT = {
    "HTML & CSS Foundations": [
        ("Introduction to HTML",
         "HTML (HyperText Markup Language) is the standard language used to create web pages. "
         "It describes the structure of a page using elements represented by tags, such as "
         "<h1> for headings, <p> for paragraphs, and <img> for images. Every HTML document "
         "starts with a <!DOCTYPE html> declaration, followed by <html>, <head>, and <body> "
         "sections. The <head> holds metadata like the page title, while the <body> holds "
         "everything visible to the user. Understanding HTML is the first step to building "
         "any website, since it forms the skeleton that CSS and JavaScript build upon.",
         "https://www.youtube.com/embed/UB1O30fR-EE"),
        ("Structuring a Web Page",
         "A well-structured web page uses semantic HTML elements to organize content clearly. "
         "Tags like <header>, <nav>, <main>, <section>, <article>, and <footer> describe the "
         "purpose of each part of the page, which helps both browsers and search engines "
         "understand your content. For example, a typical page might have a <header> with a "
         "logo and navigation menu, a <main> section containing the primary content, and a "
         "<footer> with contact details and links. Using semantic structure also improves "
         "accessibility for users relying on screen readers.", None),
        ("Styling with CSS",
         "CSS (Cascading Style Sheets) controls how HTML elements look on the page — colors, "
         "fonts, spacing, borders, and layout. CSS rules consist of a selector (which elements "
         "to style) and a declaration block (which properties to change). For example, "
         "'p { color: blue; font-size: 16px; }' makes all paragraphs blue with 16-pixel text. "
         "CSS can be added inline, in a <style> tag, or in a separate .css file linked with "
         "<link rel='stylesheet'>. Keeping styles in a separate file is best practice since it "
         "separates content from presentation and makes maintenance easier.", None),
        ("Responsive Layouts with Flexbox",
         "Flexbox is a CSS layout model designed to arrange items in a row or column and "
         "distribute space between them efficiently, even when their size is unknown. Setting "
         "'display: flex' on a container turns its direct children into flex items. Properties "
         "like 'justify-content' control horizontal alignment, 'align-items' controls vertical "
         "alignment, and 'flex-wrap' allows items to move to a new line on smaller screens. "
         "Flexbox is widely used for navigation bars, card layouts, and centering content, and "
         "is a key tool for building responsive designs that adapt to different screen sizes.", None),
    ],
    "JavaScript Essentials": [
        ("Variables & Data Types",
         "JavaScript variables store data that can be used and changed throughout a program. "
         "You declare them using 'let', 'const', or the older 'var'. 'let' allows reassignment, "
         "while 'const' creates a value that cannot be reassigned. JavaScript has several core "
         "data types: strings (text), numbers, booleans (true/false), arrays (ordered lists), "
         "objects (key-value pairs), and special values like null and undefined. Understanding "
         "these types is essential because JavaScript is loosely typed — variables can change "
         "type as a program runs.",
         "https://www.youtube.com/embed/W6NZfCO5SIk"),
        ("Functions & Scope",
         "Functions are reusable blocks of code that perform a specific task. They can take "
         "input through parameters and return a result using the 'return' keyword. JavaScript "
         "supports several function styles including function declarations, function "
         "expressions, and arrow functions ('() => {}'). Scope determines where a variable can "
         "be accessed — variables declared inside a function are local to it, while variables "
         "declared outside are accessible globally. Understanding scope helps prevent bugs "
         "caused by variables unexpectedly overwriting each other.", None),
        ("DOM Manipulation",
         "The DOM (Document Object Model) represents the structure of a web page as a tree of "
         "objects that JavaScript can interact with. Using methods like "
         "'document.querySelector()', you can select elements, then change their content, "
         "styles, or attributes dynamically. For example, "
         "'document.querySelector(\"h1\").textContent = \"Hello\"' changes a heading's text. "
         "Event listeners, such as 'addEventListener(\"click\", ...)', let you respond to user "
         "actions like clicks or key presses, making pages interactive rather than static.", None),
        ("Working with APIs",
         "APIs (Application Programming Interfaces) let your JavaScript code communicate with "
         "external services to fetch or send data. The 'fetch()' function is the modern way to "
         "make HTTP requests — for example, 'fetch(url).then(res => res.json())' retrieves data "
         "and parses it as JSON. Since network requests take time, JavaScript uses asynchronous "
         "patterns like Promises and 'async/await' to handle responses without freezing the "
         "page. Working with APIs is fundamental to building dynamic web apps that display "
         "real-world data.", None),
    ],
    "Python for Beginners": [
        ("Setting up Python",
         "Python is a beginner-friendly, general-purpose programming language known for its "
         "readable syntax. To get started, install Python from python.org, which also includes "
         "IDLE, a simple code editor. You can run a Python file from the terminal using "
         "'python filename.py'. Many developers also use editors like VS Code for a better "
         "coding experience with syntax highlighting and debugging tools. Once installed, "
         "typing 'print(\"Hello, World!\")' and running the file is the traditional first step "
         "in learning any language.",
         "https://www.youtube.com/embed/rfscVS0vtbw"),
        ("Variables & Loops",
         "Variables in Python store data without needing explicit type declarations — for "
         "example, 'age = 25' or 'name = \"Asha\"'. Python automatically determines the type. "
         "Loops let you repeat actions: a 'for' loop iterates over a sequence (like a list or "
         "range of numbers), while a 'while' loop repeats as long as a condition is true. For "
         "example, 'for i in range(5): print(i)' prints numbers 0 through 4. Loops are "
         "essential for processing collections of data efficiently.", None),
        ("Functions",
         "Functions in Python are defined using the 'def' keyword, followed by a name and "
         "parentheses containing any parameters. For example: "
         "'def greet(name): return f\"Hello, {name}!\"'. Functions help organize code into "
         "reusable, testable pieces, and can accept default parameter values, variable numbers "
         "of arguments, and return multiple values using tuples. Writing small, well-named "
         "functions makes programs easier to read, debug, and maintain as they grow larger.", None),
        ("Lists & Dictionaries",
         "Lists and dictionaries are two of Python's most-used data structures. A list, written "
         "as '[1, 2, 3]', is an ordered, changeable collection that can hold mixed data types "
         "and supports operations like appending, slicing, and sorting. A dictionary, written "
         "as '{\"name\": \"Asha\", \"age\": 25}', stores data as key-value pairs, allowing fast "
         "lookups by key instead of by position. Together, these structures let you model "
         "real-world data like student records, shopping carts, or configuration settings.", None),
    ],
    "SEO Basics": [
        ("How Search Engines Work",
         "Search engines like Google use automated programs called crawlers to discover and "
         "read web pages across the internet. Once crawled, pages are indexed — stored in a "
         "massive database along with information about their content. When someone searches, "
         "the engine's ranking algorithm scores indexed pages based on hundreds of factors, "
         "including relevance, content quality, site speed, and backlinks, then returns the "
         "best matches. Understanding this crawl-index-rank process is the foundation for "
         "everything else in SEO.",
         "https://www.youtube.com/embed/xsVTqzratPs"),
        ("Keyword Research",
         "Keyword research is the process of finding the exact words and phrases people type "
         "into search engines when looking for information related to your business. Good "
         "keyword research balances search volume (how many people search a term) with "
         "competition (how hard it is to rank for it). Long-tail keywords — longer, more "
         "specific phrases like 'best running shoes for flat feet' — often have lower "
         "competition and higher intent than broad terms like 'shoes'. Tools like Google "
         "Keyword Planner help identify these opportunities.", None),
        ("On-Page SEO",
         "On-page SEO refers to optimizations made directly on your website to improve "
         "rankings. Key elements include writing descriptive title tags and meta descriptions, "
         "using your target keyword naturally in headings and body text, optimizing images with "
         "descriptive alt text, and ensuring fast page load times. Content quality matters most "
         "— search engines favor pages that thoroughly and clearly answer the searcher's "
         "question over pages that simply repeat keywords.", None),
        ("Building Backlinks",
         "Backlinks are links from other websites pointing to yours, and they act as a vote of "
         "confidence in search engines' eyes — the more quality sites that link to you, the more "
         "authoritative your page appears. Effective link-building strategies include creating "
         "genuinely useful content that others want to reference, guest posting on relevant "
         "industry sites, and building relationships within your niche. Quality matters far more "
         "than quantity: a handful of links from respected, relevant sites outweighs many links "
         "from low-quality sources.", None),
    ],
    "Intro to Data Analysis": [
        ("What is Data Science",
         "Data science combines statistics, programming, and domain expertise to extract "
         "insights from data and support decision-making. A typical data science workflow "
         "includes collecting data, cleaning it (handling missing or incorrect values), "
         "exploring it to find patterns, building models or visualizations, and communicating "
         "findings clearly. Data scientists work across industries — from predicting customer "
         "churn in business to analyzing patient outcomes in healthcare — making it one of the "
         "most versatile and in-demand skill sets today.",
         "https://www.youtube.com/embed/X3paOmcrTjQ"),
        ("Working with Spreadsheets",
         "Spreadsheets like Excel or Google Sheets are often the first tool used to organize "
         "and analyze data. Core skills include sorting and filtering rows, using formulas like "
         "SUM, AVERAGE, and VLOOKUP to calculate and look up values, and building pivot tables "
         "to summarize large datasets by category. Spreadsheets are especially useful for "
         "smaller datasets and quick exploratory analysis before moving to more powerful tools "
         "like Python or SQL for larger-scale work.", None),
        ("Intro to Statistics",
         "Statistics provides the mathematical foundation for interpreting data correctly. Key "
         "concepts include measures of central tendency (mean, median, mode) that describe a "
         "typical value, and measures of spread (range, variance, standard deviation) that "
         "describe how much values vary. Understanding distributions — how data points are "
         "spread out — helps identify outliers and patterns. A solid grasp of basic statistics "
         "prevents common mistakes, like confusing correlation with causation.", None),
        ("Data Visualization Basics",
         "Data visualization turns numbers into charts and graphs that are easier for humans to "
         "interpret at a glance. Choosing the right chart type matters: line charts work well "
         "for trends over time, bar charts compare categories, and scatter plots reveal "
         "relationships between two variables. Good visualizations avoid clutter, use clear "
         "labels, and highlight the key insight rather than showing every possible detail. "
         "Tools like Excel, Tableau, and Python's matplotlib library are commonly used to build "
         "these visuals.", None),
    ],
    "Computer Fundamentals": [
        ("Parts of a Computer",
         "A computer is made up of hardware components that work together to process "
         "information. The CPU (Central Processing Unit) acts as the brain, executing "
         "instructions. RAM (memory) temporarily stores data the CPU needs quickly, while "
         "storage devices like SSDs or hard drives hold data permanently. The motherboard "
         "connects all components, and peripherals like the keyboard, mouse, and monitor allow "
         "users to interact with the system. Understanding these basic parts helps troubleshoot "
         "issues and make informed decisions when buying or upgrading a computer.",
         "https://www.youtube.com/embed/BwLzoi5DeGA"),
        ("Operating System Basics",
         "The operating system (OS) — like Windows, macOS, or Linux — manages a computer's "
         "hardware and software resources, providing a platform for other programs to run. It "
         "handles tasks like memory management, file storage, and running multiple programs at "
         "once. Users interact with the OS through a graphical interface (windows, icons, "
         "menus) or a command line. Learning basic OS navigation, such as managing settings and "
         "installing software, is an essential digital skill.", None),
        ("File Management",
         "Good file management keeps your digital work organized and easy to find. This "
         "includes creating a logical folder structure, using clear and consistent file names, "
         "and regularly backing up important files. Operating systems provide file explorers "
         "(File Explorer on Windows, Finder on macOS) to copy, move, rename, and delete files. "
         "Understanding file types and extensions (like .docx, .pdf, .jpg) also helps you know "
         "which programs can open a given file.", None),
        ("Using the Internet Safely",
         "Using the internet safely means protecting your personal information and devices "
         "from threats. Key practices include using strong, unique passwords for each account, "
         "enabling two-factor authentication where available, being cautious of suspicious "
         "links or email attachments (phishing), and keeping software updated to patch security "
         "vulnerabilities. Being mindful of what personal information you share on public sites "
         "and social media also reduces the risk of identity theft or scams.", None),
    ],
}


with app.app_context():
    updated_count = 0
    for course_title, lessons in LESSON_CONTENT.items():
        course = Course.query.filter_by(title=course_title).first()
        if not course:
            print(f"Course not found, skipping: {course_title}")
            continue

        for lesson_title, content_text, video_url in lessons:
            lesson = Lesson.query.filter_by(course_id=course.id, title=lesson_title).first()
            if not lesson:
                print(f"Lesson not found, skipping: {lesson_title}")
                continue

            lesson.content_text = content_text
            if video_url:
                lesson.content_url = video_url
                lesson.content_type = "video"

            updated_count += 1
            print(f"Updated: {course_title} -> {lesson_title}")

    db.session.commit()
    print(f"\nDone. Updated {updated_count} lessons.")
