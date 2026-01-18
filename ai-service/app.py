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

model = SentenceTransformer("all-MiniLM-L6-v2")

# =============================
# Constants & Configuration
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
# Utility Functions
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
    found = set()
    for skill in SKILLS:
        if skill in text:
            found.add(skill)
    return sorted(found)

# =============================
# Scoring Functions
# =============================
def skill_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    return len(set(resume_skills) & set(jd_skills)) / len(jd_skills)

def role_alignment_score(resume_text, jd_text):
    resume_hits = sum(1 for r in ROLE_KEYWORDS if r in resume_text)
    jd_hits = sum(1 for r in ROLE_KEYWORDS if r in jd_text)
    if jd_hits == 0:
        return 0.0
    return min(resume_hits / jd_hits, 1.0)

def experience_score(text):
    years = re.findall(r"(\d+)\+?\s*years", text)
    if not years:
        return 0.2
    max_years = max(map(int, years))
    return min(max_years / 5, 1.0)

def semantic_similarity_score(text1, text2):
    embeddings = model.encode([text1, text2])
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]
    return float(similarity)

# =============================
# API Endpoint
# =============================
@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    resume_file = request.files.get("resume")
    jd_text = request.form.get("job_description", "")

    if not resume_file or not jd_text:
        return jsonify({"error": "resume and job_description required"}), 400

    # 🔒 File validation
    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    resume_file.seek(0, 2)
    file_size = resume_file.tell()
    resume_file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify({"error": "File size must be under 2MB"}), 400

    # -----------------------------
    # Text Processing
    # -----------------------------
    resume_text = extract_text_from_pdf(resume_file)
    resume_text = normalize_text(clean_text(resume_text))
    jd_text = normalize_text(clean_text(jd_text))

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = sorted(set(resume_skills) & set(jd_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))

    # -----------------------------
    # Individual Scores
    # -----------------------------
    skill_score = skill_match_score(resume_skills, jd_skills)
    semantic_score = semantic_similarity_score(resume_text, jd_text)
    role_score = role_alignment_score(resume_text, jd_text)
    exp_score = experience_score(resume_text)

    # -----------------------------
    # Final Weighted Score
    # -----------------------------
    final_score = (
        0.40 * skill_score +
        0.30 * semantic_score +
        0.20 * role_score +
        0.10 * exp_score
    )

    # -----------------------------
    # Recommendations
    # -----------------------------
    recommendations = []
    if missing_skills:
        recommendations.append(
            "Consider strengthening experience with: " + ", ".join(missing_skills)
        )

    if final_score >= 0.75:
        recommendations.append("Strong alignment with the role requirements.")
    elif final_score >= 0.5:
        recommendations.append("Partial alignment. Enhancing skills or clarity may improve the match.")
    else:
        recommendations.append("Limited alignment. Review role expectations and resume focus.")

    # -----------------------------
    # Response
    # -----------------------------
    return jsonify({
        "final_score": round(final_score * 100, 2),
        "skill_match_score": round(skill_score * 100, 2),
        "semantic_similarity": round(semantic_score * 100, 2),
        "role_alignment_score": round(role_score * 100, 2),
        "experience_score": round(exp_score * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations
    })

# =============================
# Run Server (DEPLOYMENT SAFE)
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)