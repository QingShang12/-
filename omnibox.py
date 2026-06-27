#!/usr/bin/env python3
"""Omnibox: one tiny, batteries-included CLI for everyday text, JSON, files, hashes, and HTTP."""
from __future__ import annotations

import argparse, hashlib, http.server, json, re, sys
from pathlib import Path
from socketserver import TCPServer


def stream(paths):
    files = [Path(p) for p in paths] or [Path("-")]
    for path in files:
        if str(path) == "-":
            yield "<stdin>", sys.stdin.read()
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    yield str(child), child.read_text(errors="ignore")
        else:
            yield str(path), path.read_text(errors="ignore")


def grep(pattern, paths, ignore_case=False):
    rx = re.compile(pattern, re.I if ignore_case else 0)
    for name, text in stream(paths):
        for no, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                print(f"{name}:{no}:{line}")


def jget(expr):
    data = json.load(sys.stdin)
    for part in filter(None, expr.split(".")):
        data = data[int(part)] if isinstance(data, list) else data[part]
    print(json.dumps(data, ensure_ascii=False, indent=2))


def digest(algo, paths):
    for name, text in stream(paths):
        h = hashlib.new(algo); h.update(text.encode())
        print(f"{h.hexdigest()}  {name}")


def serve(directory=".", port=8000):
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=directory, **k)
    with TCPServer(("", port), handler) as httpd:
        print(f"Serving {Path(directory).resolve()} at http://127.0.0.1:{port}")
        httpd.serve_forever()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(required=True)
    g = sub.add_parser("grep", help="regex search files, dirs, or stdin"); g.add_argument("pattern"); g.add_argument("paths", nargs="*"); g.add_argument("-i", action="store_true"); g.set_defaults(func=lambda a: grep(a.pattern, a.paths, a.i))
    j = sub.add_parser("json", help="read stdin JSON and select a dotted path"); j.add_argument("path"); j.set_defaults(func=lambda a: jget(a.path))
    h = sub.add_parser("hash", help="hash files, dirs, or stdin"); h.add_argument("paths", nargs="*"); h.add_argument("-a", default="sha256", choices=hashlib.algorithms_available); h.set_defaults(func=lambda a: digest(a.a, a.paths))
    s = sub.add_parser("serve", help="serve a directory over HTTP"); s.add_argument("directory", nargs="?", default="."); s.add_argument("-p", type=int, default=8000); s.set_defaults(func=lambda a: serve(a.directory, a.p))
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
