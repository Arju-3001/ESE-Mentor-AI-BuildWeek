from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

from ai import ask_ai, read_pdf

from config import SECRET_KEY

from database import get_connection

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename
import fitz

import os

app = Flask(__name__)

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

connection.commit()
connection.close()

app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.secret_key = SECRET_KEY


@app.route("/")
def home():
    return render_template("index.html")


from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["name"]
            session["email"] = user["email"]

            return redirect(url_for("dashboard"))

        return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        connection = get_connection()
        cursor = connection.cursor()

        # Check duplicate email
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            return "Email already registered. Please login."

        # Insert new user
        cursor.execute(
            "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )

        connection.commit()
        connection.close()

        return "Registration Successful!"

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/prelims")
def prelims():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("prelims.html")


@app.route("/network-theory")
def network_theory():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("network-theory.html")


@app.route("/mcq")
def mcq():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("mcq.html")

@app.route("/ai-chat", methods=["GET", "POST"])
def ai_chat():

    if "user" not in session:
        return redirect(url_for("login"))

    question = ""
    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        prompt = f"""
You are ESE Mentor AI.

Rules:
- Answer only Engineering Services Examination (ESE/IES) questions.
- Explain concepts in simple language.
- Give formulas wherever required.
- For theory questions, answer in UPSC/ESE Mains style.
- For objective questions, explain why the correct option is correct.
- If the question is not related to ESE, Electronics, Electrical, Mechanical, Civil, Computer Science, Mathematics, Physics or Engineering, politely reply:
'I am ESE Mentor AI. Please ask ESE-related questions.'

Question:
{question}
"""

        answer = ask_ai(question)

    return render_template(
        "ai-chat.html",
        question=question,
        answer=answer
    )


@app.route("/upload-pdf", methods=["GET", "POST"])
def upload_pdf():

    if "user" not in session:
        return redirect(url_for("login"))

    summary = ""
    answer = ""

    if request.method == "POST":

        pdf = request.files["pdf"]

        if pdf.filename == "":
            return "Please select a PDF."

        filename = secure_filename(pdf.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        pdf.save(filepath)

        pdf_text = read_pdf(filepath)

        session["pdf_text"] = pdf_text

        summary = ask_ai(
            "Summarize the following ESE notes in simple points:\n\n" + pdf_text[:12000]
        )

    return render_template(
    "upload-pdf.html",
    summary=summary,
    answer=answer,
    mcqs=""
)


@app.route("/ask-pdf", methods=["POST"])
def ask_pdf():

    if "user" not in session:
        return redirect(url_for("login"))

    if "pdf_text" not in session:
        return "Please upload a PDF first."

    question = request.form["question"]

    prompt = f"""
You are ESE Mentor AI.

Answer ONLY from the uploaded PDF.

PDF Content:
{session['pdf_text'][:12000]}

Question:
{question}
"""

    answer = ask_ai(prompt)

    summary = ask_ai(
        "Summarize the uploaded PDF in simple points:\n\n" +
        session["pdf_text"][:12000]
    )

    return render_template(
        "upload-pdf.html",
        summary=summary,
        answer=answer
    )


@app.route("/generate-mcq", methods=["POST"])
def generate_mcq():

    if "user" not in session:
        return redirect(url_for("login"))

    if "pdf_text" not in session:
        return "Please upload a PDF first."

    prompt = f"""
You are an ESE Mentor AI.

Generate 10 multiple-choice questions from the uploaded PDF.

Rules:
- Each question should have 4 options (A, B, C, D).
- Clearly mention the correct answer after each question.
- Questions should be suitable for ESE Prelims.

PDF Content:
{session["pdf_text"][:12000]}
"""

    mcqs = ask_ai(prompt)

    summary = ask_ai(
        "Summarize the uploaded PDF in simple points:\n\n" +
        session["pdf_text"][:12000]
    )

    return render_template(
        "upload-pdf.html",
        summary=summary,
        answer="",
        mcqs=mcqs
    )


@app.route("/mains-answer", methods=["GET", "POST"])
def mains_answer():

    if "user" not in session:
        return redirect(url_for("login"))

    answer = ""

    if request.method == "POST":

        question = request.form["question"]

        prompt = f"""
You are an ESE Mentor AI.

Write a UPSC Engineering Services (ESE) Mains answer.

Format:

1. Definition
2. Explanation
3. Formula (if required)
4. Advantages
5. Applications
6. Conclusion

Question:
{question}
"""

        answer = ask_ai(prompt)

    return render_template(
        "mains-answer.html",
        answer=answer
    )

if __name__ == "__main__":
    app.run(debug=True)