from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Replace if needed
DEEPSEEK_API_KEY = "sk-f7d5f5137a3440eab5fc562d78d3ffe5"  # Set this in Render dashboard

@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.json
    user_prompt = f"Class {data['class']} {data['subject']} - Topic: {data['topic']}\nQuestion: {data['query']}\nAnswer only from NCERT textbook."

    try:
        response = requests.post(DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",  # adjust if needed
                "messages": [
                    {"role": "system", "content": "You are an AI tutor for NCERT Class 11 & 12. Only answer using NCERT textbooks."},
                    {"role": "user", "content": user_prompt}
                ]
            }
        )

        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]

        return jsonify({
            "response": ai_response,
            "topic": data["topic"],
            "class": data["class"],
            "subject": data["subject"],
            "createdAt": request.date if hasattr(request, 'date') else "2025-06-06"
        })

    except Exception as e:
        return jsonify({"message": "Something went wrong", "error": str(e)}), 500

@app.route("/api/doubts", methods=["POST"])
def submit_doubt():
    data = request.json
    # Optional: Save to database or just echo back
    return jsonify({"message": "Doubt submitted successfully!", "data": data})

@app.route("/api/doubts", methods=["GET"])
def recent_doubts():
    # Optional: Return fake doubts for now
    return jsonify([])

@app.route("/", methods=["GET"])
def home():
    return "NCERT AI Backend is Live!"
