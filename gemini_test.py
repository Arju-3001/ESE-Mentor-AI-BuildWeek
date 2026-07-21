import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.1-flash-lite")

response = model.generate_content(
    "Explain Thevenin Theorem in simple words."
)

print(response.text)