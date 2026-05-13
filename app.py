from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

AI_OPS_BASE_URL = "https://ai-ops-command-center.onrender.com"

SYSTEM_PROMPT = """
You are Synthetic Voice Agent Command Center.

You are a smart voice assistant for Matthew Jolley.
You help with AI automation, remote AI/ML jobs, workflow systems, emails, business automation, and portfolio projects.

You do not claim to be conscious.
You act like a synthetic intelligence operating system: calm, strategic, direct, and useful.

When the user asks for jobs, call the job search tool.
When the user asks about emails/messages, call the email assistant tool.
When the user asks about workflow logs, call the events tool.
When the user asks general questions, answer clearly.
"""

def search_jobs(keyword):
    try:
        url = f"{AI_OPS_BASE_URL}/api/jobs"
        response = requests.get(url, params={"keyword": keyword}, timeout=20)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def email_assistant(message):
    try:
        url = f"{AI_OPS_BASE_URL}/api/email-assistant"
        response = requests.post(url, json={"message": message}, timeout=20)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_events():
    try:
        url = f"{AI_OPS_BASE_URL}/api/events"
        response = requests.get(url, timeout=20)
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

    if "job" in lower or "machine learning" in lower or "ai engineer" in lower:
        tool_result = search_jobs(user_message)

    elif "email" in lower or "message" in lower or "spam" in lower:
        tool_result = email_assistant(user_message)

    elif "event" in lower or "log" in lower or "workflow" in lower:
        tool_result = get_events()

    prompt = f"""
User said:
{user_message}

Tool result:
{tool_result}

Answer in a helpful voice assistant style.
Be direct.
If jobs were found, summarize the best results.
If email/message was analyzed, explain the classification and suggested action.
If workflow logs were returned, summarize them.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return jsonify({
        "reply": response.output_text,
        "tool_result": tool_result
    })

@app.route("/api/health")
def health():
    return jsonify({"status": "Synthetic Voice Agent online"})

if __name__ == "__main__":
    app.run(debug=True)
