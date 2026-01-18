import os
from app import analyze_resume_function  # logic refactored into a function

K = 5
THRESHOLD = 0.7  # relevance threshold

results = []

for resume_file in os.listdir("evaluation_resumes"):
    score = analyze_resume_function(
        resume_path=f"evaluation_resumes/{resume_file}",
        job_description=open("jd.txt").read()
    )
    results.append((resume_file, score))

# Sort by score descending
results.sort(key=lambda x: x[1], reverse=True)

# Label relevance
relevant = [(r, 1 if s >= THRESHOLD else 0) for r, s in results]

# Top K
top_k = relevant[:K]

precision_at_k = sum(label for _, label in top_k) / K
recall_at_k = sum(label for _, label in top_k) / sum(label for _, label in relevant)

f1_at_k = (
    2 * precision_at_k * recall_at_k /
    (precision_at_k + recall_at_k)
    if precision_at_k + recall_at_k > 0 else 0
)

print("Precision@K:", round(precision_at_k, 2))
print("Recall@K:", round(recall_at_k, 2))
print("F1@K:", round(f1_at_k, 2))