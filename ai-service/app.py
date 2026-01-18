from flask import Flask, request, jsonify
import re
import PyPDF2
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# =============================
# App Initialization
# =============================
app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]
)

model = None  # Lazy-loaded to avoid OOM on free tier

# =============================
# Configuration
# =============================
MAX_FILE_SIZE_MB = 2

SKILL_SYNONYMS = {
    "js": "javascript",
    "nodejs": "node",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "postgres": "postgresql",
    "reactjs": "react",
    "expressjs": "express"
}

SKILLS = [
    "python", "java", "c++", "sql", "html", "css", "javascript",
    "react", "node", "express", "mongodb", "flask",
    "aws", "docker", "machine learning", "nlp"
]

ROLE_KEYWORDS = [
    "intern", "developer", "engineer",
    "software", "backend", "frontend", "full stack"
]

# =============================
# Utilities
# =============================
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

def normalize_text(text):
    for alias, canonical in SKILL_SYNONYMS.items():
        text = text.replace(alias, canonical)
    return text

def extract_skills(text):
    return sorted({skill for skill in SKILLS if skill in text})

# =============================
# Scoring
# =============================
def skill_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    return len(set(resume_skills) & set(jd_skills)) / len(jd_skills)

def role_alignment_score(resume_text, jd_text):
    resume_hits = sum(1 for r in ROLE_KEYWORDS if r in resume_text)
    jd_hits = sum(1 for r in ROLE_KEYWORDS if r in jd_text)
    return min(resume_hits / jd_hits, 1.0) if jd_hits else 0.0

def experience_score(text):
    years = re.findall(r"(\d+)\+?\s*years", text)
    return min(max(map(int, years)) / 5, 1.0) if years else 0.2

def semantic_similarity_score(text1, text2):
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = model.encode([text1, text2])
    return float(
        cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    )

# =============================
# API
# =============================
@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    resume_file = request.files.get("resume")
    jd_text = request.form.get("job_description", "")

    if not resume_file or not jd_text:
        return jsonify({"error": "resume and job_description required"}), 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    resume_file.seek(0, 2)
    if resume_file.tell() > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify({"error": "File too large"}), 400
    resume_file.seek(0)

    resume_text = normalize_text(clean_text(extract_text_from_pdf(resume_file)))
    jd_text = normalize_text(clean_text(jd_text))

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    skill_score = skill_match_score(resume_skills, jd_skills)
    semantic_score = semantic_similarity_score(resume_text, jd_text)
    role_score = role_alignment_score(resume_text, jd_text)
    exp_score = experience_score(resume_text)

    final_score = (
        0.40 * skill_score +
        0.30 * semantic_score +
        0.20 * role_score +
        0.10 * exp_score
    )

    return jsonify({
        "final_score": round(final_score * 100, 2),
        "skill_match_score": round(skill_score * 100, 2),
        "semantic_similarity": round(semantic_score * 100, 2),
        "role_alignment_score": round(role_score * 100, 2),
        "experience_score": round(exp_score * 100, 2),
        "matched_skills": sorted(set(resume_skills) & set(jd_skills)),
        "missing_skills": sorted(set(jd_skills) - set(resume_skills))
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})