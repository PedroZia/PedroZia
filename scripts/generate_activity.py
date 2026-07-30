#!/usr/bin/env python3
"""Draw recent public activity from the Events API.

A second scheduled pipeline, independent of generate_stats.py and using a
different data source. Outputs:
  recent-activity.svg

Same visual language as ascii.svg and the stat graphics — grey ink, monospace,
SMIL reveal with a cursor. No third-party services and no dependencies beyond
the standard library.

Env:
  GITHUB_TOKEN  optional — bumps rate limit from 60 to 5000 req/h
  GH_LOGIN      user to summarise (default: PedroZia)
  OUT_DIR       where to write (default: repository root)
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

EVENTS_API = "https://api.github.com/users/{login}/events/public"

LIGHT = dict(data="#6e7681", emph="#424a53", dim="#8c959f",
             rule="#d8dee4", surface="#ffffff")
DARK = dict(data="#c9d1d9", emph="#f0f6fc", dim="#8b949e",
            rule="#30363d", surface="#0d1117")
MONO = ("ui-monospace,SFMono-Regular,Menlo,Consolas,"
        "&apos;Liberation Mono&apos;,monospace")

WIDTH = 620
LEFT = 34
REVEAL = 1.30
MAX_EVENTS = 10


def relative(iso):
    ts = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    mins = int(delta.total_seconds() // 60)
    if mins < 2:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs}h ago"
    days = hrs // 24
    if days < 30:
        return f"{days}d ago"
    return ts.strftime("%b %d")


def style():
    def block(t):
        return (f".d-f{{fill:{t['data']}}}.d-s{{stroke:{t['data']}}}"
                f".e-f{{fill:{t['emph']}}}.m-f{{fill:{t['dim']}}}"
                f".u-s{{stroke:{t['rule']}}}.r{{stroke:{t['surface']}}}")
    return (f"<style>{block(LIGHT)}"
            f"@media(prefers-color-scheme:dark){{{block(DARK)}}}</style>")


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" font-family="{MONO}">'
            + style())


def fade(delay, dur=0.45):
    return (f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.2f}s" dur="{dur}s" fill="freeze"/>')


def label(x, y, text, size=11, cls="m-f", anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}"{a}'
            f'{extra}>{text}</text>')


def event_text(event):
    t = event["type"]
    repo = event["repo"]["name"]
    payload = event.get("payload", {})

    if t == "PushEvent":
        count = payload.get("size", 0) or 0
        branch = (payload.get("ref") or "").removeprefix("refs/heads/")
        if branch:
            return f"pushed {count} commit{'s' if count != 1 else ''} to {repo} ({branch})"
        return f"pushed to {repo}"
    if t == "PullRequestEvent":
        action = payload.get("action", "updated")
        return f"{action} a pull request in {repo}"
    if t == "IssuesEvent":
        action = payload.get("action", "updated")
        return f"{action} an issue in {repo}"
    if t == "CreateEvent":
        ref_type = payload.get("ref_type", "repository")
        ref = payload.get("ref", "")
        if ref:
            return f"created {ref_type} {ref} in {repo}"
        return f"created {ref_type} in {repo}"
    if t == "WatchEvent":
        return f"starred {repo}"
    if t == "ForkEvent":
        return f"forked {repo}"
    if t == "ReleaseEvent":
        tag = (payload.get("release") or {}).get("tag_name", "")
        return f"released {tag} in {repo}"
    if t == "DeleteEvent":
        ref_type = payload.get("ref_type", "branch")
        ref = payload.get("ref", "")
        return f"deleted {ref_type} {ref} in {repo}"
    if t == "PullRequestReviewEvent":
        return f"reviewed a pull request in {repo}"
    if t == "IssueCommentEvent":
        return f"commented on an issue in {repo}"
    return f"{t.lower().replace('event', '')} on {repo}"


def fetch_events(login, token=None):
    url = EVENTS_API.format(login=login)
    headers = {"User-Agent": f"{login}-profile-activity",
               "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def draw_activity(events):
    if not events:
        H = 46
        p = [head(WIDTH, H)]
        p.append(f'<g opacity="0">{fade(0.10)}'
                 + label(LEFT, 12, "RECENT ACTIVITY", 9, "m-f",
                         extra=' letter-spacing="1.3"') + '</g>')
        p.append(f'<g opacity="0">{fade(0.25)}'
                 + label(LEFT, 32, "no recent public activity", 11, "m-f")
                 + '</g>')
        p.append("</svg>")
        return "".join(p)

    rows = len(events)
    H = 26 + rows * 22 + 6
    colw = WIDTH - LEFT - 30
    time_w = 64

    p = [head(WIDTH, H)]
    p.append(f'<g opacity="0">{fade(0.10)}'
             + label(LEFT, 12, "RECENT ACTIVITY", 9, "m-f",
                     extra=' letter-spacing="1.3"') + '</g>')

    for ri, event in enumerate(events):
        y = 26 + ri * 22
        text = event_text(event)[:68]
        when = relative(event["created_at"])

        p.append(f'<g opacity="0">{fade(0.20 + ri * 0.05)}'
                 + label(LEFT, y + 8, text, 11, "e-f")
                 + label(LEFT + colw - 4, y + 8, when, 10, "m-f", "end")
                 + '</g>')

    p.append("</svg>")
    return "".join(p)


def write_if_changed(path, svg):
    old = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    if old == svg:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return True


def main():
    login = os.environ.get("GH_LOGIN", "PedroZia")
    token = os.environ.get("GITHUB_TOKEN")
    out_dir = os.environ.get("OUT_DIR", ".")

    events = fetch_events(login, token)
    events = events[:MAX_EVENTS]

    svg = draw_activity(events)
    path = os.path.join(out_dir, "recent-activity.svg")
    changed = write_if_changed(path, svg)
    print(f"{len(events)} events, {changed and 'updated' or 'no change'}")


if __name__ == "__main__":
    main()
