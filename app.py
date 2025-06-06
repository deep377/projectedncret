from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Environment variables for security
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Must be set in environment

@app.route("/api/explain", methods=["POST"])
def explain():
    # Validate required fields
    required_fields = {'class', 'subject', 'topic', 'query'}
    if not request.json or not required_fields.issubset(request.json):
        return jsonify({"error": "Missing required fields: class, subject, topic, query"}), 400
        
    data = request.json
    user_prompt = f"Class {data['class']} {data['subject']} - Topic: {data['topic']}\nQuestion: {data['query']}\nAnswer only from NCERT textbook."

    try:
        # Make API request
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are an AI tutor for NCERT Class 11 & 12. Only answer using NCERT textbooks."
                    },
                    {"role": "user", "content": user_prompt}
                ]
            },
            timeout=30  # Add timeout
        )

        # Handle API errors
        if response.status_code != 200:
            return jsonify({
                "error": "DeepSeek API error",
                "status_code": response.status_code,
                "message": response.text
            }), 502

        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]

        return jsonify({
            "response": ai_response,
            "topic": data["topic"],
            "class": data["class"],
            "subject": data["subject"],
            "createdAt": datetime.utcnow().isoformat()  # Fixed timestamp
        })

    except KeyError:
        return jsonify({"error": "Invalid response format from DeepSeek API"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection failed: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/api/doubts", methods=["POST"])
def submit_doubt():
    if not request.json or 'doubt' not in request.json:
        return jsonify({"error": "Missing 'doubt' field"}), 400
        
    return jsonify({
        "message": "Doubt submitted successfully!",
        "doubt": request.json['doubt']
    })

@app.route("/api/doubts", methods=["GET"])
def recent_doubts():
    # Placeholder implementation
    return jsonify({
        "doubts": [
            {"id": 1, "question": "Sample question about photosynthesis?"},
            {"id": 2, "question": "How to solve quadratic equations?"}
        ]
    })

@app.route("/", methods=["GET"])
def home():
    return "NCERT AI Backend is Live!"

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
