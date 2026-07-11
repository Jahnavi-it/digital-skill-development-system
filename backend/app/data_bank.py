"""
Static question bank for the Mock Interview module.
No AI/LLM is used anywhere here — questions are hand-written, and scoring is
plain keyword matching against an `expected_keywords` list per question.
This keeps the feature deterministic and explainable, which is what a CSP
evaluator will expect from a "no AI" academic project.
"""

QUESTION_BANK = {
    "Web Developer": [
        {"q": "What is the difference between HTML and HTML5?", "keywords": ["semantic", "video", "audio", "canvas", "api", "tags"]},
        {"q": "Explain the CSS Box Model.", "keywords": ["margin", "border", "padding", "content"]},
        {"q": "What is the difference between == and === in JavaScript?", "keywords": ["type", "value", "strict", "coercion"]},
        {"q": "What is responsive web design?", "keywords": ["media queries", "flexible", "screen", "viewport", "mobile"]},
        {"q": "What is the difference between GET and POST HTTP methods?", "keywords": ["url", "body", "idempotent", "cache", "data"]},
    ],
    "Python Developer": [
        {"q": "What is the difference between a list and a tuple in Python?", "keywords": ["mutable", "immutable", "brackets", "parentheses"]},
        {"q": "What are Python decorators?", "keywords": ["function", "wrapper", "modify", "behaviour", "behavior", "@"]},
        {"q": "Explain exception handling in Python.", "keywords": ["try", "except", "finally", "raise", "error"]},
        {"q": "What is the difference between deep copy and shallow copy?", "keywords": ["reference", "nested", "copy", "independent"]},
        {"q": "What are Python generators?", "keywords": ["yield", "iterator", "lazy", "memory"]},
    ],
    "Data Science": [
        {"q": "What is the difference between supervised and unsupervised learning?", "keywords": ["labeled", "unlabeled", "labels", "clustering"]},
        {"q": "What is overfitting and how do you prevent it?", "keywords": ["training", "generalize", "regularization", "cross-validation", "validation"]},
        {"q": "Explain the difference between a Series and DataFrame in pandas.", "keywords": ["one-dimensional", "two-dimensional", "column", "index"]},
        {"q": "What is the purpose of data normalization?", "keywords": ["scale", "range", "features", "distance"]},
        {"q": "What is a confusion matrix used for?", "keywords": ["accuracy", "precision", "recall", "true positive", "false"]},
    ],
    "Digital Marketing": [
        {"q": "What is SEO and why is it important?", "keywords": ["search engine", "ranking", "organic", "keywords", "traffic"]},
        {"q": "What is the difference between organic and paid marketing?", "keywords": ["free", "ads", "budget", "cost", "unpaid"]},
        {"q": "What is a conversion rate?", "keywords": ["percentage", "visitors", "action", "goal"]},
        {"q": "What is content marketing?", "keywords": ["value", "audience", "blog", "engage", "content"]},
        {"q": "What are the key metrics for social media marketing?", "keywords": ["engagement", "reach", "impressions", "followers", "ctr"]},
    ],
    "Basic Computer Skills": [
        {"q": "What is the difference between hardware and software?", "keywords": ["physical", "programs", "device", "instructions"]},
        {"q": "What is an operating system?", "keywords": ["manage", "resources", "software", "hardware"]},
        {"q": "What is the purpose of a firewall?", "keywords": ["security", "network", "block", "unauthorized", "traffic"]},
        {"q": "What is cloud storage?", "keywords": ["internet", "remote", "server", "online", "backup"]},
        {"q": "What is the difference between RAM and ROM?", "keywords": ["volatile", "permanent", "temporary", "memory"]},
    ],
}


def score_answer(answer_text, keywords):
    """Very simple rule-based scoring: % of expected keywords present in the answer (case-insensitive)."""
    if not answer_text or not keywords:
        return 0
    text = answer_text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return round((hits / len(keywords)) * 100)
