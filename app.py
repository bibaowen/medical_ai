from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os
import pymysql

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Optional DB config if you still use prompt modifiers
DB_HOST = "db5018172480.hosting-data.io"
DB_USER = "dbu3245801"
DB_PASS = "Biba2@portmore"
DB_NAME = "dbs14409615"

app = Flask(__name__)

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
    return "✅ Medical AI API is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    note = data.get("note", "").strip()
    specialty = data.get("specialty", "general")

    if not note:
        return jsonify({"error": "Missing clinical note"}), 400

    modifier = get_prompt_modifier(specialty)

    # 👇 Structured but free-text prompt
    prompt = f"""
You are a highly trained medical AI. Given the following clinical case, provide a detailed diagnostic breakdown using plain structured headings:

1. Differential Diagnosis
2. Pathophysiology Summary
3. Workup
4. Management
5. Disposition

Only return medically formatted text — do not explain your role.

{modifier}

CASE:
\"\"\"{note}\"\"\"
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical expert that outputs only structured diagnostic reasoning text."},
                {"role": "user", "content": prompt}
            ]
        )

        full_response = response.choices[0].message.content.strip()
        print("✅ AI Output:\n", full_response)
        return jsonify({"full_response": full_response})

    except Exception as e:
        return jsonify({"error": f"Error during OpenAI call: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
