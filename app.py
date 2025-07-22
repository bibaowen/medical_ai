from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import openai
import os
import psycopg2
from datetime import datetime

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_HOST = "db5018172480.hosting-data.io"
DB_USER = "dbu3245801"
DB_PASS = "Biba2@portmore"
DB_NAME = "dbs14409615"

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Analysis Comparison</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .container { display: flex; gap: 20px; }
        .panel { flex: 1; border: 1px solid #ccc; padding: 10px; border-radius: 8px; background: #f9f9f9; }
        h2 { font-size: 18px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h1>Analysis Comparison</h1>
    <div class="container">
        <div class="panel">
            <h2>Analysis ID: {{ record1.id }}</h2>
            <strong>Patient:</strong> {{ record1.patient_name }}<br>
            <strong>Specialty:</strong> {{ record1.specialty }}<br>
            <strong>Date:</strong> {{ record1.created_at }}<br><br>
            <pre>{{ record1.analysis }}</pre>
        </div>
        <div class="panel">
            <h2>Analysis ID: {{ record2.id }}</h2>
            <strong>Patient:</strong> {{ record2.patient_name }}<br>
            <strong>Specialty:</strong> {{ record2.specialty }}<br>
            <strong>Date:</strong> {{ record2.created_at }}<br><br>
            <pre>{{ record2.analysis }}</pre>
        </div>
    </div>
</body>
</html>
"""

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
    return "✅ Medical AI API with history & comparison dashboard is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    note = data.get("note", "").strip()
    specialty = data.get("specialty", "general")

    if not note:
        return jsonify({"error": "Missing clinical note"}), 400

    modifier = get_prompt_modifier(specialty)
    patient_name = note.split(",")[0].strip() if "," in note else "Unknown"

    prompt = f"""
You are a highly trained clinical decision support AI. Analyze the following clinical case and return your diagnostic reasoning using these 10 structured sections:

1. 🧠 Differential Diagnosis
2. 🧬 Pathophysiology Integration
3. 🧪 Diagnostic Workup
4. 💊 Treatment and Medications
5. ⚖️ Risk Stratification & Clinical Judgment
6. 🩺 Management of Chronic Conditions
7. 🧼 Infection Consideration & Antibiotics
8. 💓 Disposition & Follow-Up
9. 📝 Red Flags or Missed Diagnoses
10. 📋 Clinical Guidelines Integration

{modifier}

CASE:
""" + note +"""
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

        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clinical_analyses (patient_name, specialty, note, analysis)
                VALUES (%s, %s, %s, %s)
            """, (patient_name, specialty, note, full_response))
            conn.commit()

        return jsonify({"full_response": full_response})

    except Exception as e:
        return jsonify({"error": f"Error during processing: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def history():
    patient_name = request.args.get("patient_name", "").strip()
    if not patient_name:
        return jsonify({"error": "Missing patient_name"}), 400
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                SELECT id, patient_name, specialty, created_at FROM clinical_analyses
                WHERE patient_name = %s
                ORDER BY created_at DESC
            """, (patient_name,))
            return jsonify(cur.fetchall())
    except Exception as e:
        return jsonify({"error": f"DB error: {str(e)}"}), 500

@app.route('/compare', methods=['GET'])
def compare():
    id1 = request.args.get("id1")
    id2 = request.args.get("id2")
    render = request.args.get("render", "html")

    if not id1 or not id2:
        return jsonify({"error": "Missing id1 or id2"}), 400

    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM clinical_analyses WHERE id IN (%s, %s)", (id1, id2))
            records = cur.fetchall()

            if len(records) != 2:
                return jsonify({"error": "One or both records not found"}), 404

            records = sorted(records, key=lambda x: x['id'])
            if render == "json":
                return jsonify({"comparison": records})
            else:
                return render_template_string(HTML_TEMPLATE, record1=records[0], record2=records[1])

    except Exception as e:
        return jsonify({"error": f"DB compare error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
