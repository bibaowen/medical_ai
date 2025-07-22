from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
import os
import pymysql

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database connection for specialty-specific prompt modifiers
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

    prompt = f"""
You are a highly trained clinical decision support AI. Analyze the following clinical case and return your diagnostic reasoning using these 10 structured sections:

1. 🧠 Differential Diagnosis  
List common, atypical, and potentially life-threatening causes. Justify each based on symptoms, history, and exam findings.

2. 🧬 Pathophysiology Integration  
Explain how current presentation links to the patient’s chronic or acute conditions.

3. 🧪 Diagnostic Workup  
List tests/labs/imaging. Explain rationale, what you’re looking for, and how it guides management.

4. 💊 Treatment and Medications  
Detailed treatment plan with medications (dose, route, frequency). Include rationale, alternatives, monitoring, and dose adjustments.

5. ⚖️ Risk Stratification & Clinical Judgment  
Assess acuity and escalation needs. Identify red flags or signs of deterioration.

6. 🩺 Management of Chronic Conditions  
Explain how chronic diseases should be managed/adjusted during this episode.

7. 🧼 Infection Consideration & Antibiotics  
If infection suspected, recommend empiric treatment with spectrum, dosing, and de-escalation strategy.

8. 💓 Disposition & Follow-Up  
Recommend setting (outpatient vs inpatient), follow-up timeline, specialists needed, and discharge criteria.

9. 📝 Red Flags or Missed Diagnoses  
Mention critical but rare diagnoses not to miss and how to rule them out.

10. 📋 Clinical Guidelines Integration  
Cite relevant clinical guidelines (e.g., AHA, IDSA) and how they inform your approach.

{modifier}

CASE:
\"\"\"{note}\"\"\"
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical expert that returns only formatted diagnostic analysis."},
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
