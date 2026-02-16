# 📊 Earnings Call Research Tool (Option B)

A web-based research tool that analyzes **earnings call transcripts / management commentary**
and generates **structured financial insights** using AI.

This project is built as part of a Full Stack Developer assignment.
The focus is on **reliability, clarity, and usability**, not raw performance.

---

## 🚀 What This Tool Does

The system allows users to:

1. Upload an earnings call transcript (PDF or TXT)
2. Extract text from the document
3. Run AI analysis on the transcript
4. Generate structured research output including:
   - Management tone
   - Confidence level
   - Key positives
   - Key concerns
   - Forward guidance
   - Capacity utilization trends
   - Growth initiatives

---

## 🧠 Research Output (Option B)

**Generated Insights:**
- Management tone: optimistic / cautious / neutral / pessimistic
- Confidence level: high / medium / low
- 3–5 key positives
- 3–5 key concerns
- Forward guidance (revenue, margin, capex)
- Capacity utilization trends
- 2–3 growth initiatives

If any information is **not mentioned** in the transcript, it is explicitly marked as  
**"Not mentioned"** (no hallucination).

---

## 🧩 Supported Input Files

| File Type | Supported |
|-----------|-----------|
|   PDF     |    ✅    |
|   TXT     |    ✅    |

> 💡 **Important Note (Indian Financial PDFs):**  
> Some PDFs have encoding issues.  
> If PDF extraction fails, convert PDF → TXT:
> - Open PDF in Chrome
> - Press `Ctrl + A` → `Ctrl + C`
> - Paste into Notepad
> - Save as `.txt`
> - Upload the TXT file

---

## ⚙️ Tech Stack

- **Backend:** Python, Flask
- **AI Model:** Groq (LLaMA – Free Tier)
- **PDF/Text Processing:** pdfplumber, PyPDF2, pdfminer.six
- **Frontend:** HTML, CSS (Jinja templates)
- **Deployment:** Render (Free Plan)

---

## 📁 Project Structure
option-b-research-tool/
│
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── .env
│
├── utils/
│ ├── pdf_reader.py
│ └── concall_summary.py
│
├── templates/
│ ├── index.html
│ └── result.html
│
└── uploads/


---

## 🛠️ How to Run This Project Locally

### 1️⃣ Clone the repository
```bash

git clone <your-github-repo-link>
cd option-b-research-tool

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

python app.py

http://localhost:5000



