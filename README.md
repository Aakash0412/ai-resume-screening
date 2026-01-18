
# AI-Powered Resume Screening Platform (Local Setup)

## Architecture
React (Frontend) -> Node.js + Express (API Gateway) -> Python Flask (AI Service)

## Prerequisites
- Node.js >= 18
- Python >= 3.9

## How to Run (Local)
### 1) Start AI Service
```
cd ai-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
AI service runs on http://localhost:5001

### 2) Start Backend
```
cd backend
npm install
node index.js
```
Backend runs on http://localhost:5000

### 3) Start Frontend
```
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:5173

## Notes
- This is a minimal MVP for local execution.
- PDF parsing supports text-based PDFs.
