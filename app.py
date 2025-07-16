from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os
import pymysql

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# MySQL config
DB_HOST = "db5018172480.hosting-data.io"
DB_USER = "dbu3245801"
DB_PASS = "Biba2@portmore"
DB_NAME = "dbs14409615"

app = Flask(__name__)

# Get specialty-specific prompt modifier
def get_prompt_modifier(specialty_slug):
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT prompt_modifier FROM specialties WHERE slug = %s", (specialty_slug,))
            row = cur.fetchone()
            return row[0] if row and row[0] else ""
    except Exception as e:
        print("DB error getting specialty modifier:", e)
    return ""

@app.route('/')
def home():
    return "✅ Medical AI is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    note = data.get("note", "").strip()
    specialty = data.get("specialty", "general")

    if not note:
        return jsonify({"error": "Missing case note."}), 400

    prompt_modifier = get_prompt_modifier(specialty)

    prompt = f"""
You are a medical diagnostic assistant. Based on the following clinical case, generate a detailed structured analysis including:

- Differential Diagnosis
- Pathophysiology Summary
- Workup Plan
- Management Plan
- Disposition

Use clear headings and medical reasoning. Format your response in professional paragraph and bullet list format.

{prompt_modifier}

CASE:
{note}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a clinical assistant generating full diagnostic impressions."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        return jsonify({"full_response": content})

    except Exception as e:
        return jsonify({"error": f"Error during OpenAI call: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
