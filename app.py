from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

AI_OPS_BASE_URL = "https://ai-ops-command-center.onrender.com"

SYSTEM_PROMPT = """
You are Synthetic GPT Voice Assistant.

You are an advanced everyday AI assistant similar to ChatGPT with voice capabilities.

You help with:
- general conversation
- life questions
- coding
- writing
- brainstorming
- automation
- productivity
- AI workflows
- business ideas
- remote jobs
- email analysis
- organization
- planning

You speak naturally and intelligently.

You also have tools available:
- AI Ops job search
- workflow logs
- email assistant
- automation APIs

Only use tools when needed.
For normal conversation, answer directly like ChatGPT.
"""

def search_jobs(keyword):
    try:
        response = requests.get(
            f"{AI_OPS_BASE_URL}/api/jobs",
            params={"keyword": keyword},
            timeout=20
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_email(message):
    try:
        response = requests.post(
            f"{AI_OPS_BASE_URL}/api/email-assistant",
            json={"message": message},
            timeout=20
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_workflow_logs():
    try:
        response = requests.get(
            f"{AI_OPS_BASE_URL}/api/events",
            timeout=20
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/agent", methods=["POST"])
def agent():

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    lower = user_message.lower()

    tool_result = None

    if any(word in lower for word in ["job", "career", "hiring", "machine learning", "ai engineer"]):
        tool_result = search_jobs(user_message)

    elif any(word in lower for word in ["email", "spam", "message", "phishing"]):
        tool_result = analyze_email(user_message)

    elif any(word in lower for word in ["workflow", "event", "automation log", "logs"]):
        tool_result = get_workflow_logs()

    if not client:
        return jsonify({
            "reply": "OpenAI API key is missing. Add OPENAI_API_KEY to Render environment variables.",
            "tool_result": tool_result
        })

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",

            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
User message:
{user_message}

Tool result:
{tool_result}

Respond naturally like an advanced voice assistant.
Only reference tool results if relevant.
"""
                }
            ]
        )

        return jsonify({
            "reply": response.output_text,
            "tool_result": tool_result
        })

    except Exception as e:

        return jsonify({
            "reply": f"There was an error connecting to the AI model: {str(e)}",
            "error": str(e)
        })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "Synthetic GPT Voice Assistant online"
    })

if __name__ == "__main__":
    app.run(debug=True)
