import google.generativeai as genai
import os
from dotenv import load_dotenv
import fitz

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-3.1-flash-lite")


def ask_ai(question):

    prompt = f"""
You are ESE Mentor AI.

Rules:
- Answer only Engineering Services Examination (ESE/IES) questions.
- Explain concepts in simple language.
- Give formulas wherever required.
- Write UPSC/ESE style answers.
- If the question is not related to engineering or ESE, reply:
'I am ESE Mentor AI. Please ask ESE-related questions.'

Question:
{question}
"""

    response = model.generate_content(prompt)

    return response.text

def read_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text