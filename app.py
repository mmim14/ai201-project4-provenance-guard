"""Provenance Guard — Flask application.

Milestone 3 skeleton: the POST /submit endpoint and the first (semantic) signal.
Structural heuristics, confidence aggregation, transparency labeling, the audit
log, and the appeals workflow are stubbed for later milestones (see planning.md).
"""

import asyncio
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request

import audit
import scoring
from signals.semantic import analyze_semantic
from signals.structural import analyze_structural

load_dotenv()

app = Flask(__name__)


async def _run_signals(text: str) -> tuple[float, float]:
    """Run the semantic (LLM) and structural (local) signals concurrently.

    The structural signal is CPU-bound and synchronous, so it runs in a worker
    thread while the semantic signal awaits the Groq API.
    """
    return await asyncio.gather(
        analyze_semantic(text),
        asyncio.to_thread(analyze_structural, text),
    )


def transparency_label(score: float) -> str:
    """Map a 0.0-1.0 confidence score to a plain-language attribution label.

    0.0-0.4 = High-Confidence Human, 0.4-0.6 = Uncertain,
    0.6-1.0 = High-Confidence AI (see planning.md).
    """
    if score < 0.4:
        return "High-Confidence Human"
    if score < 0.6:
        return "Uncertain"
    return "High-Confidence AI"

WELCOME_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Provenance Guard</title>
  <style>
    body { font-family: system-ui, sans-serif; text-align: center;
           margin: 3rem auto; max-width: 640px; color: #222; }
    h1 { margin-bottom: 0.25rem; }
    p.tagline { color: #666; margin-top: 0; }
    img { border-radius: 12px; margin: 1.5rem 0; max-width: 100%;
          box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
    code { background: #f2f2f2; padding: 0.15rem 0.4rem; border-radius: 4px; }
    a.cta { display: inline-block; margin-top: 0.5rem; padding: 0.6rem 1.4rem;
            font-weight: 600; color: #fff; background: #2563eb;
            border-radius: 6px; text-decoration: none; }
    a.cta:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <h1>🛡️ Welcome to Provenance Guard</h1>
  <p class="tagline">Multi-signal AI-vs-human text attribution.</p>
  <img src="https://cataas.com/cat?width=400" alt="A random cat">
  <p>Head to the <code>/submit</code> endpoint to submit a response for
     classification.</p>
  <a class="cta" href="/submit">Go to /submit &rarr;</a>
</body>
</html>"""

SUBMIT_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Submit &middot; Provenance Guard</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 3rem auto;
           max-width: 640px; color: #222; }
    h1 { margin-bottom: 1rem; }
    a.back { color: #2563eb; text-decoration: none; }
    label { display: block; font-weight: 600; margin: 0.75rem 0 0.25rem; }
    textarea, input[type=text] { width: 100%; padding: 0.5rem; font: inherit;
           border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
    textarea { min-height: 120px; resize: vertical; }
    button { margin-top: 1rem; padding: 0.6rem 1.4rem; font: inherit;
           font-weight: 600; color: #fff; background: #2563eb; border: none;
           border-radius: 6px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    button:disabled { background: #9db8ef; cursor: not-allowed; }
    pre { background: #f2f2f2; padding: 1rem; border-radius: 8px;
          overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <a class="back" href="/">&larr; Home</a>
  <h1>Submit a response</h1>

  <form id="submit-form">
    <label for="creator_id">Creator ID</label>
    <input type="text" id="creator_id" name="creator_id" placeholder="e.g. user123" required>
    <label for="text">Text to classify</label>
    <textarea id="text" name="text" placeholder="Paste the text here..." required></textarea>
    <button type="submit">Submit</button>
  </form>

  <pre id="result" hidden></pre>

  <script>
    const form = document.getElementById("submit-form");
    const result = document.getElementById("result");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const button = form.querySelector("button");
      button.disabled = true;
      result.hidden = false;
      result.textContent = "Classifying...";
      try {
        const res = await fetch("/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            creator_id: document.getElementById("creator_id").value,
            text: document.getElementById("text").value,
          }),
        });
        const data = await res.json();
        result.textContent = "HTTP " + res.status + "\\n\\n" +
          JSON.stringify(data, null, 2);
      } catch (err) {
        result.textContent = "Request failed: " + err;
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(WELCOME_PAGE), 200


@app.route("/submit", methods=["GET"])
def submit_form():
    return render_template_string(SUBMIT_PAGE), 200


@app.route("/submit", methods=["POST"])
def submit():
    """Accept raw text + creator_id, run the semantic signal, return a stub result.

    Later milestones will add the structural signal, weighted confidence scoring,
    the transparency label, and the audit-log write before responding.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON."}), 400

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "'text' is required and must be a non-empty string."}), 400
    if not isinstance(creator_id, str) or not creator_id.strip():
        return jsonify({"error": "'creator_id' is required and must be a non-empty string."}), 400

    submission_id = str(uuid.uuid4())

    # Run the semantic (LLM) and structural (local) signals concurrently.
    try:
        semantic_score, structural_score = asyncio.run(_run_signals(text))
    except Exception as exc:  # noqa: BLE001 - surface any signal failure to the client for now
        return jsonify({"error": f"Signal analysis failed: {exc}"}), 502

    # Aggregate into a final confidence score (50/50 weighted average).
    confidence_score = scoring.combine(semantic_score, structural_score)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "creator_id": creator_id,
        "submission_id": submission_id,
        "label": transparency_label(confidence_score),
        "semantic_score": round(semantic_score, 4),
        "structural_score": round(structural_score, 4),
        "confidence_score": round(confidence_score * 100, 1),
        "status": "classified",
    }

    # Write the audit-log entry before responding.
    audit.append_entry(record)

    return jsonify(record), 200


@app.route("/log", methods=["GET"])
def log():
    """Return the most recent audit-log entries (newest first) as JSON.

    Optional query param `limit` (default 20) caps how many entries are returned.
    """
    try:
        limit = int(request.args.get("limit", 20))
    except (TypeError, ValueError):
        return jsonify({"error": "'limit' must be an integer."}), 400
    limit = max(1, min(limit, 100))

    entries = audit.read_recent(limit)
    return jsonify({"count": len(entries), "entries": entries}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
