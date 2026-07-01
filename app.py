"""Provenance Guard — Flask application.

Milestone 3 skeleton: the POST /submit endpoint and the first (semantic) signal.
Structural heuristics, confidence aggregation, transparency labeling, the audit
log, and the appeals workflow are stubbed for later milestones (see planning.md).
"""

import asyncio
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from signals.semantic import analyze_semantic

load_dotenv()

app = Flask(__name__)


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

    # Run the async semantic signal from this sync route.
    try:
        semantic_score = asyncio.run(analyze_semantic(text))
    except Exception as exc:  # noqa: BLE001 - surface any signal failure to the client for now
        return jsonify({"error": f"Semantic analysis failed: {exc}"}), 502

    # TODO(M4): structural signal, weighted aggregation, transparency label.
    # TODO(M5): write audit-log entry before responding.
    return jsonify(
        {
            "uuid": submission_id,
            "creator_id": creator_id,
            "signals": {"semantic": semantic_score},
            "status": "classified",
        }
    ), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
