from flask import Flask, render_template, request, redirect, url_for, flash
import os
import uuid
from dotenv import load_dotenv

from utils.pdf_reader import extract_text_from_pdf, extract_text_from_txt
from utils.concall_summary import generate_concall_summary, format_summary_for_display

# Load environment variables FIRST
load_dotenv()

app = Flask(__name__)

# Stable secret key (important for deployment)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "option-b-secret-key")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt"}
MAX_LLM_CHARS = 5000  # Safe limit for Groq free tier


def allowed_file(filename):
    """Check allowed file extensions"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("❌ No file selected. Please upload a PDF or TXT.")
        return redirect(url_for("index"))

    file = request.files["file"]

    if not file.filename or file.filename == "":
        flash("❌ No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("❌ Only PDF and TXT files are supported.")
        return redirect(url_for("index"))

    file_ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    try:
        file.save(file_path)

        # Extract text
        if file_ext == "pdf":
            success, text = extract_text_from_pdf(file_path)
            file_type = "PDF"
        else:
            success, text = extract_text_from_txt(file_path)
            file_type = "TXT"

        if not success:
            flash(
                f"⚠️ {file_type} extraction failed. "
                f"For Indian financial PDFs, upload TXT for best accuracy."
            )
            return redirect(url_for("index"))

        # Guard: text must be meaningful
        if not text or len(text.strip()) < 50:
            flash("⚠️ Document text is too short for analysis.")
            return redirect(url_for("index"))

        # Limit text for LLM
        text = text[:MAX_LLM_CHARS]

        # Generate AI summary
        success, summary = generate_concall_summary(text)

        if not success:
            flash(f"⚠️ AI processing failed: {summary}")
            return redirect(url_for("index"))

        display_summary = format_summary_for_display(summary)

        return render_template(
            "result.html",
            filename=file.filename,
            file_type=file_type,
            summary=display_summary
        )

    except Exception as e:
        flash(f"❌ Unexpected error: {str(e)}")
        return redirect(url_for("index"))

    finally:
        # Always delete uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
