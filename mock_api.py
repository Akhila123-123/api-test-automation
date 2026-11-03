"""Tiny local REST API (standard library only) used as a test target.

Endpoints
  GET    /posts            -> list of posts (supports ?userId=)
  GET    /posts/<id>       -> one post, 404 if missing
  POST   /posts            -> create a post (needs title and body), 201
  DELETE /posts/<id>       -> delete a post, 200, 404 if missing

Run:  python mock_api.py            (listens on 127.0.0.1:8000)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

POSTS = {
    1: {"id": 1, "userId": 1, "title": "first post", "body": "hello world"},
    2: {"id": 2, "userId": 1, "title": "second post", "body": "testing apis"},
    3: {"id": 3, "userId": 2, "title": "third post", "body": "regression suite"},
}
NEXT_ID = 4


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload=None):
        body = json.dumps(payload if payload is not None else {}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _post_id(self, path):
        parts = path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "posts" and parts[1].isdigit():
            return int(parts[1])
        return None

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/posts":
            posts = list(POSTS.values())
            user = parse_qs(url.query).get("userId")
            if user:
                posts = [p for p in posts if str(p["userId"]) == user[0]]
            return self._send(200, posts)
        pid = self._post_id(url.path)
        if pid is not None:
            if pid in POSTS:
                return self._send(200, POSTS[pid])
            return self._send(404, {"error": "not found"})
        self._send(404, {"error": "unknown route"})

    def do_POST(self):
        global NEXT_ID
        if urlparse(self.path).path != "/posts":
            return self._send(404, {"error": "unknown route"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})
        if not data.get("title") or not data.get("body"):
            return self._send(400, {"error": "title and body are required"})
        post = {"id": NEXT_ID, "userId": data.get("userId", 1),
                "title": data["title"], "body": data["body"]}
        POSTS[NEXT_ID] = post
        NEXT_ID += 1
        self._send(201, post)

    def do_DELETE(self):
        pid = self._post_id(urlparse(self.path).path)
        if pid is None or pid not in POSTS:
            return self._send(404, {"error": "not found"})
        del POSTS[pid]
        self._send(200, {})

    def log_message(self, fmt, *args):  # keep test output quiet
        pass


def run(host="127.0.0.1", port=8000):
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
