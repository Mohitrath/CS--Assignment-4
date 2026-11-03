from __future__ import annotations

import html
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "comments.sqlite3"
CSS_FILE = BASE_DIR / "static" / "style.css"
MAX_AUTHOR_LENGTH = 50
MAX_COMMENT_LENGTH = 1000
MAX_REQUEST_BYTES = 16 * 1024
HOST = "127.0.0.1"
PORT = 5000


def connect_db(database: Path = DATABASE) -> sqlite3.Connection:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database: Path = DATABASE) -> None:
    with connect_db(database) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )"""
        )


def save_comment(author: str, body: str, database: Path = DATABASE) -> None:
    """Insert raw comment text. SQL parameters prevent SQL injection."""
    with connect_db(database) as db:
        db.execute(
            "INSERT INTO comments (author, body) VALUES (?, ?)",
            (author, body),
        )


def get_comments(database: Path = DATABASE) -> list[sqlite3.Row]:
    with connect_db(database) as db:
        return db.execute(
            "SELECT id, author, body, created_at FROM comments ORDER BY id DESC"
        ).fetchall()


def delete_comments(database: Path = DATABASE) -> None:
    with connect_db(database) as db:
        db.execute("DELETE FROM comments")


def render_comment_cards(comments: Iterable[sqlite3.Row | dict], secure: bool) -> str:
    """Render comments; secure=True encodes data for an HTML text node.

    The vulnerable branch is intentionally unsafe for the classroom demo.
    Names are escaped in both modes so the demonstrated flaw is only the body.
    """
    cards: list[str] = []
    for comment in comments:
        author = html.escape(str(comment["author"]), quote=True)
        body = str(comment["body"])
        if secure:
            body = html.escape(body, quote=True)
        created_at = html.escape(str(comment["created_at"]), quote=True)
        cards.append(
            '<article class="comment-card">'
            f'<div class="comment-meta"><strong>{author}</strong>'
            f'<time>{created_at}</time></div>'
            f'<div class="comment-body">{body}</div>'
            '</article>'
        )
    return "\n".join(cards) if cards else '<div class="empty-state">No comments yet. Submit one above.</div>'


def page_shell(title: str, content: str, notice: str = "") -> bytes:
    safe_title = html.escape(title, quote=True)
    notice_html = f'<div class="notice success">{html.escape(notice)}</div>' if notice else ""
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} | Web Server Security Lab</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header class="site-header"><div class="container header-inner">
    <a class="brand" href="/">Web Server Security Lab</a>
    <nav aria-label="Main navigation">
      <a href="/">Home</a><a href="/vulnerable">Vulnerable</a><a href="/secure">Secured</a>
    </nav>
  </div></header>
  <main class="container">{notice_html}{content}</main>
  <footer class="site-footer"><div class="container">Local classroom demonstration · Stored XSS · SQLite</div></footer>
</body></html>"""
    return document.encode("utf-8")


def render_home() -> bytes:
    content = """<section class="hero">
  <p class="eyebrow">Cyber Security · IT-30001</p>
  <h1>Stored Cross-Site Scripting (XSS)</h1>
  <p class="lead">A comment application that compares unsafe HTML rendering with context-aware output encoding.</p>
  <div class="assignment-card"><strong>Assigned work: Mohit Kumar</strong>
    <span>Vulnerability: Stored XSS</span><span>Functionality: Comment submission and display</span>
    <span>Mitigation: Context-aware output encoding</span>
  </div>
</section>
<section class="two-column">
  <article class="panel danger-panel"><span class="tag danger-tag">Part A · Intentionally vulnerable</span>
    <h2>Vulnerable comments</h2><p>Comments are stored and later inserted into the page as raw HTML.</p>
    <a class="button danger-button" href="/vulnerable">Open vulnerable page</a>
  </article>
  <article class="panel safe-panel"><span class="tag safe-tag">Part B · Mitigated</span>
    <h2>Secured comments</h2><p>The same stored comment is displayed as harmless text using HTML output encoding.</p>
    <a class="button safe-button" href="/secure">Open secured page</a>
  </article>
</section>
<section class="panel instructions"><h2>Local demonstration flow</h2>
  <ol><li>Open the vulnerable page and submit the classroom test payload.</li>
  <li>Reload the vulnerable page: the stored script demonstrates the flaw again.</li>
  <li>Open the secured page: the same stored value appears as literal text and does not execute.</li></ol>
  <p class="small-note"><strong>Safety:</strong> This server binds only to localhost. Use it only with your own local application and test payloads.</p>
  <form method="post" action="/reset" onsubmit="return confirm('Delete all comments in this local demo database?');">
    <button class="button secondary-button" type="submit">Reset demo comments</button>
  </form>
</section>"""
    return page_shell("Home", content)


def render_comments_page(secure: bool, notice: str = "") -> bytes:
    if secure:
        label = '<span class="tag safe-tag">Mitigated · Part B</span>'
        heading = "Comment board — secured"
        explanation = (
            "Comments are saved in the same SQLite database. Jinja is not required here: "
            "the server HTML-encodes special characters before placing the value in this HTML text context."
        )
        callout = (
            '<section class="panel success-box"><strong>Mitigation:</strong> Context-aware output encoding. '
            'The code uses <code>html.escape(comment)</code> for an HTML text node; it does not insert the value as markup.</section>'
        )
        action = "/submit-secure"
        button_class = "safe-button"
    else:
        label = '<span class="tag danger-tag">Intentionally vulnerable · Part A</span>'
        heading = "Comment board — vulnerable"
        explanation = (
            "Comments are stored in SQLite. The comment body is then inserted into the page as raw HTML without encoding."
        )
        callout = (
            '<section class="panel warning-box"><strong>Lab note:</strong> This page intentionally contains the Stored XSS flaw. '
            'Do not deploy it publicly or enter real personal information.</section>'
        )
        action = "/submit-vulnerable"
        button_class = "danger-button"

    comment_form = f"""<section class="panel"><h2>Leave a comment</h2>
  <form method="post" action="{action}" class="comment-form">
    <label for="author">Name <span>(optional, up to 50 characters)</span></label>
    <input id="author" name="author" maxlength="50" placeholder="Mohit Kumar">
    <label for="body">Comment <span>(maximum 1,000 characters)</span></label>
    <textarea id="body" name="body" maxlength="1000" rows="4" required placeholder="Write a comment..."></textarea>
    <button class="button {button_class}" type="submit">Save comment</button>
  </form></section>"""
    comments = get_comments()
    cards = render_comment_cards(comments, secure=secure)
    comments_html = (
        f'<section class="comments-section"><div class="section-title-row"><h2>Stored comments</h2>'
        f'<span class="count">{len(comments)} total</span></div>{cards}</section>'
    )
    content = (
        f'<section class="page-heading">{label}<h1>{heading}</h1><p>{explanation}</p></section>'
        + callout + comment_form + comments_html
    )
    return page_shell(heading, content, notice)


class StoredXSSHandler(BaseHTTPRequestHandler):
    server_version = "StoredXSSLab/1.0"

    def log_message(self, _format: str, *args) -> None:
        # Keep the console focused on startup and errors during the demo.
        return

    def send_html(self, content: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API name
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        notice = ""
        if query.get("saved") == ["1"]:
            notice = "Comment saved to the local SQLite database."
        elif query.get("reset") == ["1"]:
            notice = "All demo comments have been deleted."
        elif query.get("error") == ["empty"]:
            notice = "Please enter a comment before submitting."
        elif query.get("error") == ["length"]:
            notice = "The name or comment exceeds the allowed length."

        if path == "/":
            self.send_html(render_home())
        elif path == "/vulnerable":
            self.send_html(render_comments_page(secure=False, notice=notice))
        elif path == "/secure":
            self.send_html(render_comments_page(secure=True, notice=notice))
        elif path == "/style.css":
            try:
                css = CSS_FILE.read_bytes()
            except OSError:
                self.send_html(b"CSS file not found", status=404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(css)))
            self.end_headers()
            self.wfile.write(css)
        else:
            self.send_html(b"<h1>404 - Page not found</h1>", status=404)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API name
        path = urlparse(self.path).path
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_html(b"Invalid request", status=400)
            return
        if length < 0 or length > MAX_REQUEST_BYTES:
            self.send_html(b"Request too large", status=413)
            return
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        fields = parse_qs(raw, keep_blank_values=True)

        if path == "/reset":
            delete_comments()
            self.redirect("/?reset=1")
            return

        if path not in ("/submit-vulnerable", "/submit-secure"):
            self.send_html(b"<h1>404 - Page not found</h1>", status=404)
            return

        author = fields.get("author", [""])[0].strip() or "Anonymous"
        body = fields.get("body", [""])[0].strip()
        destination = "/vulnerable" if path == "/submit-vulnerable" else "/secure"
        if not body:
            self.redirect(f"{destination}?error=empty")
            return
        if len(author) > MAX_AUTHOR_LENGTH or len(body) > MAX_COMMENT_LENGTH:
            self.redirect(f"{destination}?error=length")
            return

        # Raw text is intentionally stored to show that escaping belongs at output.
        save_comment(author, body)
        self.redirect(f"{destination}?saved=1")


def main() -> None:
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), StoredXSSHandler)
    print("Stored XSS lab is running locally.")
    print(f"Open http://{HOST}:{PORT} in your browser.")
    print("Press Ctrl+C in this window to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the local demo...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
