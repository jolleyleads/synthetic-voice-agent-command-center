from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

AI_OPS_BASE_URL = "https://ai-ops-command-center.onrender.com"

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

def fallback_reply(user_message, tool_result):
    if tool_result and "jobs" in tool_result:
        jobs = tool_result.get("jobs", [])
        if jobs:
            top = jobs[0]
            return f"I found {len(jobs)} jobs. The first one is {top.get('title')} at {top.get('company')}."
        return "I searched for jobs, but no jobs came back."

    return "Agent is online. I can search jobs, check workflows, and connect to your AI Ops Command Center."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/agent", methods=["POST"])
def agent():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    tool_result = None

    if "job" in user_message.lower() or "machine learning" in user_message.lower() or "ai" in user_message.lower():
        tool_result = search_jobs(user_message)

    if not client:
        return jsonify({
            "reply": fallback_reply(user_message, tool_result),
            "tool_result": tool_result,
            "warning": "OPENAI_API_KEY not found"
        })

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
You are a voice AI assistant connected to an AI Ops Command Center.

User request:
{user_message}

Tool result:
{tool_result}

Give a clear spoken-style answer.
"""
        )

        return jsonify({
            "reply": response.output_text,
            "tool_result": tool_result
        })

    except Exception as e:
        return jsonify({
            "reply": fallback_reply(user_message, tool_result),
            "tool_result": tool_result,
            "error": str(e)
        })

@app.route("/api/health")
def health():
    return jsonify({"status": "Synthetic Voice Agent online"})

if __name__ == "__main__":
    app.run(debug=True)
