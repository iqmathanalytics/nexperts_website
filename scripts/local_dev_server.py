# -*- coding: utf-8 -*-
"""Serve the site root with root `_redirects` applied (ordered rules, first match).

Use when you open the site locally without Netlify CLI. From repo root:

    python scripts/local_dev_server.py

Then visit http://127.0.0.1:8080/courses/az-104 etc.
"""
from __future__ import annotations

import argparse
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "_redirects"
_RULE = re.compile(r"^(\S+)\s+(\S+)\s+(200|301|302|404)(?:\s|$)")


def norm_path(path: str) -> str:
    path = unquote(path)
    if "?" in path:
        path = path.split("?", 1)[0]
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path or "/"


def load_rules() -> list[tuple[str, str, int]]:
    rules: list[tuple[str, str, int]] = []
    if not REDIRECTS.is_file():
        return rules
    for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
        s = line.split("#")[0].strip()
        if not s or s.startswith("#"):
            continue
        m = _RULE.match(s)
        if not m:
            continue
        src, dst, code_s = m.group(1), m.group(2), m.group(3)
        if ":" in src:
            continue
        rules.append((norm_path(src), dst, int(code_s)))
    return rules


def _under_root(path: Path) -> bool:
    try:
        path.relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


class Handler(BaseHTTPRequestHandler):
    rules: list[tuple[str, str, int]] = []

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_HEAD(self) -> None:  # noqa: N802
        self._dispatch()

    def _dispatch(self) -> None:
        parsed = urlparse(self.path)
        path = norm_path(parsed.path)
        qs = f"?{parsed.query}" if parsed.query else ""

        for src, dst, code in self.rules:
            if path != src:
                continue
            if code in (301, 302):
                if dst.startswith("http://") or dst.startswith("https://"):
                    loc = dst
                else:
                    loc = dst if dst.startswith("/") else "/" + dst
                    loc = loc + qs
                self.send_response(code)
                self.send_header("Location", loc)
                self.end_headers()
                return
            if code == 200:
                rel = dst.lstrip("/")
                file_path = (ROOT / rel).resolve()
                if not _under_root(file_path) or not file_path.is_file():
                    self.send_error(404)
                    return
                ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
                clen = file_path.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(clen))
                self.end_headers()
                if self.command == "GET":
                    self.wfile.write(file_path.read_bytes())
                return

        rel = path.lstrip("/")
        if not rel:
            rel = "index.html"
        file_path = (ROOT / rel).resolve()
        if not _under_root(file_path):
            self.send_error(403)
            return
        if file_path.is_dir():
            idx = file_path / "index.html"
            file_path = idx if idx.is_file() else None
        if not file_path or not file_path.is_file():
            self.send_error(404)
            return
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        clen = file_path.stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(clen))
        self.end_headers()
        if self.command == "GET":
            self.wfile.write(file_path.read_bytes())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def main() -> None:
    ap = argparse.ArgumentParser(description="Static server with _redirects (local dev).")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    Handler.rules = load_rules()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving {ROOT} with _redirects — http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
