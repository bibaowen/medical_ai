from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os
import json
import re
import pymysql

# Load OpenAI API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# MySQL config (edit if needed)
DB_HOST = "db5018172480.hosting-data.io"
DB_USER = "dbu3245801"
DB_PASS = "Biba2@portmore"
DB_NAME = "dbs14409615"

app = Flask(__name__)

# Get specialty modifier from DB
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
    return "✅ AI Medical Parser API is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    note = data.get("note", "").strip()
    specialty = data.get("specialty", "general")

    if not note:
        return jsonify({"error": "Missing case note."}), 400

    # Load any specialty-specific prompt addition
    prompt_modifier = get_prompt_modifier(specialty)

    # Build prompt for AI
    prompt = f"""
You are a clinical diagnostic assistant AI. Analyze the following patient case note and return only a valid structured JSON object with the fields below.

{prompt_modifier}

Return all fields even if unknown. Leave blank strings or empty lists where applicable.

Return only valid JSON in this format:
{{
  "name": "",
  "age": 0,
  "gender": "",
  "symptoms": [],
  "past_medical_history": [],
  "vitals": {{
    "blood_pressure": "",
    "heart_rate": "",
    "oxygen_saturation": ""
  }},
  "exam_findings": "",
  "labs": "",
  "summary": "",
  "differential_diagnosis": [],
  "suggested_tests": [],
  "management_plan": "",
  "tips": "",
  "recommendations": ""
}}

CASE NOTE:
\"\"\"{note}\"\"\"
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # switch to "gpt-4o" if preferred and allowed
            messages=[
                {"role": "system", "content": "You are a clinical AI that returns only JSON medical analysis."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()
        print("🔍 Raw AI Response:\n", content)  # optional debug log

        # Try parsing JSON directly
        try:
            return jsonify(json.loads(content))
        except json.JSONDecodeError:
            # Try extracting embedded JSON
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                json_str = match.group()
                return jsonify(json.loads(json_str))
            else:
                return jsonify({"error": "AI returned non-JSON response", "raw": content}), 500

    except Exception as e:
        return jsonify({"error": f"Error during OpenAI call: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Default port for Render
    app.run(host='0.0.0.0', port=port)


#if __name__ == '__main__':
 #   app.run(debug=True)
