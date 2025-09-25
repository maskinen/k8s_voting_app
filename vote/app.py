from flask import Flask, request, jsonify
import os, uuid, psycopg2, psycopg2.extras
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime

app = Flask(__name__)

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@db:5432/vote")
conn = psycopg2.connect(DB_URL)
conn.autocommit = True

votes_total = Counter(
    "voting_votes_total",
    "Votes by round/option",
    ["round_id","round_name","option_id","option_label"]
)
round_open = Gauge("voting_round_open", "1=open,0=closed", ["round_id"])

def q(sql, params=None, fetch="none"):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or [])
        if fetch == "one":  return cur.fetchone()
        if fetch == "all":  return cur.fetchall()

@app.get("/health")
def health(): return {"ok": True}

@app.post("/rounds")
def create_round():
    data = request.get_json(force=True)
    name = data.get("name","Round "+datetime.utcnow().isoformat())
    options = data.get("options", ["A","B"])
    rid = str(uuid.uuid4())
    q("INSERT INTO rounds(id,name) VALUES(%s,%s)", [rid,name])
    for label in options:
        q("INSERT INTO options(id,round_id,label) VALUES(gen_random_uuid(),%s,%s)", [rid,label])
    round_open.labels(rid).set(1)
    return jsonify({"round_id": rid, "name": name, "options": options}), 201

@app.post("/vote")
def vote():
    data = request.get_json(force=True)
    rid = data["round_id"]; oid = data["option_id"]
    # guard: round must be open
    r = q("SELECT id,name,ended_at FROM rounds WHERE id=%s", [rid], "one")
    if not r: return jsonify({"error":"round_not_found"}), 404
    if r["ended_at"] is not None: return jsonify({"error":"round_closed"}), 400
    o = q("SELECT id,label FROM options WHERE id=%s AND round_id=%s", [oid,rid], "one")
    if not o: return jsonify({"error":"option_not_found"}), 404

    voter_id = request.headers.get("X-Voter-Id")  # optional uniqueness
    try:
        q("INSERT INTO votes(round_id, option_id, voter_id) VALUES(%s,%s,%s)", [rid, oid, voter_id])
    except psycopg2.Error as e:
        return jsonify({"error":"duplicate_vote_or_db_error","detail":str(e)}), 400

    votes_total.labels(rid, r["name"], oid, o["label"]).inc()
    return jsonify({"ok": True})

@app.post("/rounds/<rid>/close")
def close_round(rid):
    q("UPDATE rounds SET ended_at=now() WHERE id=%s AND ended_at IS NULL", [rid])
    round_open.labels(rid).set(0)
    return {"ok": True}

@app.get("/rounds/<rid>/results")
def results(rid):
    rows = q("""
    SELECT o.id AS option_id, o.label, COUNT(v.id)::int AS votes
    FROM options o LEFT JOIN votes v ON v.option_id=o.id
    WHERE o.round_id=%s
    GROUP BY o.id,o.label
    ORDER BY votes DESC
    """,[rid], "all")
    return jsonify(rows)

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","8080")))