from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

app = Flask(__name__)

# 컨테이너 안에서 데이터를 저장할 경로 (docker-compose의 volume과 연결됨)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "blog.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 결과를 dict처럼 컬럼명으로 접근 가능하게
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", posts=posts)


@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        created_at = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        conn.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)", (title, content, created_at)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("write.html")


@app.route("/post/<int:post_id>")
def post(post_id):
    conn = get_db()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return render_template("post.html", post=post)


if __name__ == "__main__":
    init_db()
    # host="0.0.0.0" 필수: 이게 없으면 컨테이너 밖(호스트/외부)에서 절대 접속 안 됨
    app.run(host="0.0.0.0", port=5000, debug=True)