#!/usr/bin/env python3
"""근거 기반 한의학 위키 — 추천(좋아요) 집계 백엔드.

Flask + SQLite로 문서별 추천 수를 집계한다.
정적 MkDocs 사이트의 추천 버튼이 이 API를 호출한다.

사용법:
    python3 server/app.py            # 0.0.0.0:8000 에서 실행
    python3 server/app.py --port 9000
"""
import argparse
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "server", "likes.db")

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            path TEXT PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT
        )
        """
    )
    db.commit()
    db.close()


@app.route("/api/like", methods=["POST"])
def like():
    data = request.get_json(silent=True) or {}
    path = (data.get("path") or "").strip()
    if not path:
        return jsonify({"error": "path required"}), 400
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        """
        INSERT INTO likes (path, count, updated_at) VALUES (?, 1, ?)
        ON CONFLICT(path) DO UPDATE SET count = count + 1, updated_at = excluded.updated_at
        """,
        (path, now),
    )
    db.commit()
    row = db.execute("SELECT count FROM likes WHERE path = ?", (path,)).fetchone()
    return jsonify({"path": path, "count": row["count"]})


@app.route("/api/likes")
def likes():
    db = get_db()
    rows = db.execute("SELECT path, count FROM likes ORDER BY count DESC").fetchall()
    return jsonify([{"path": r["path"], "count": r["count"]} for r in rows])


@app.route("/api/rank")
def rank():
    db = get_db()
    rows = db.execute("SELECT path, count FROM likes ORDER BY count DESC, path").fetchall()
    return jsonify([{"path": r["path"], "count": r["count"]} for r in rows])


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def main():
    p = argparse.ArgumentParser(description="추천 집계 백엔드")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    init_db()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
