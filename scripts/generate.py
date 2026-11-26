#!/usr/bin/env python3
"""Generates the profile SVGs (stats, activity, languages) with a flat, GitHub-native palette.

Data sources:
  - public contribution calendar (what visitors see): https://github.com/users/<user>/contributions
  - GitHub GraphQL via the `gh` CLI (or GH_TOKEN): languages, followers, repo count

Usage: python3 scripts/generate.py [username]
"""
import html
import json
import re
import subprocess
import sys
import urllib.request
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "xXxMiltonxXx"
OUT = Path(__file__).resolve().parent.parent / "assets"
W = 840

# Flat, GitHub-dark palette (no gradients)
BG, CARD, BORDER = "#0d1117", "#161b22", "#30363d"
ACCENT = "#2f81f7"
TEXT, MUTED = "#e6edf3", "#8b949e"
LANG_COLORS = ["#2f81f7", "#3fb950", "#d29922", "#a371f7", "#db6d28", "#f778ba", "#39c5cf", "#6e7681"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def esc(s):
    return html.escape(str(s), quote=True)


def fetch_calendar():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "profile-readme-generator"})
    page = urllib.request.urlopen(req, timeout=30).read().decode()
    days = {}
    for d, cid in re.findall(r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-\d+-\d+)"', page):
        m = re.search(r'for="%s"[^>]*>(No|\d+) contributions?' % re.escape(cid), page)
        days[d] = 0 if (not m or m.group(1) == "No") else int(m.group(1))
    return OrderedDict(sorted(days.items()))


def graphql(query):
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["data"]["user"]


def fetch_profile():
    q = ('query{user(login:"%s"){followers{totalCount} repositories(first:100,ownerAffiliations:OWNER,isFork:false)'
         '{totalCount nodes{languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}' % USER)
    return graphql(q)


def streaks(days):
    vals = list(days.values())
    longest = run = 0
    for v in vals:
        run = run + 1 if v else 0
        longest = max(longest, run)
    cur, i = 0, len(vals) - 1
    if i >= 0 and vals[i] == 0:
        i -= 1  # today may not have commits yet
    while i >= 0 and vals[i]:
        cur += 1
        i -= 1
    return cur, longest


def frame(h, body, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{FONT}">
<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
{defs}
{body}
</svg>'''


def title(text, sub=""):
    s = f'<text x="32" y="44" fill="{TEXT}" font-size="18" font-weight="600">{esc(text)}</text>'
    if sub:
        s += f'<text x="{W-32}" y="44" fill="{MUTED}" font-size="13" text-anchor="end">{esc(sub)}</text>'
    return s


def stats_svg(days, prof):
    total = sum(days.values())
    active = sum(1 for v in days.values() if v)
    cur, longest = streaks(days)
    tiles = [
        (f"{total:,}", "Contributions · last year"),
        (str(active), "Active days"),
        (f"{cur}", "Current streak (days)"),
        (f"{longest}", "Longest streak (days)"),
        (str(prof["repositories"]["totalCount"]), "Repositories"),
        (str(prof["followers"]["totalCount"]), "Followers"),
    ]
    body = title("GitHub overview", f"@{USER}")
    cw, ch = (W - 64) / 3, 78
    for i, (num, label) in enumerate(tiles):
        x = 32 + (i % 3) * cw
        y = 70 + (i // 3) * (ch + 8)
        body += f'''<g style="animation:fade .6s ease both;animation-delay:{i*0.08:.2f}s">
<rect x="{x:.0f}" y="{y}" width="{cw-12:.0f}" height="{ch}" rx="12" fill="{CARD}" stroke="{BORDER}"/>
<text x="{x+20:.0f}" y="{y+40}" fill="{TEXT}" font-size="30" font-weight="700">{esc(num)}</text>
<text x="{x+20:.0f}" y="{y+62}" fill="{MUTED}" font-size="12.5">{esc(label)}</text></g>'''
    style = "<style>@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style>"
    return frame(250, style + body)


def activity_svg(days):
    items = list(days.items())
    # --- monthly bars
    months = OrderedDict()
    for d, v in items:
        months[d[:7]] = months.get(d[:7], 0) + v
    keys = list(months)[-12:]
    vals = [months[k] for k in keys]
    top = max(vals + [1])
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    body = title("Contribution activity", "per month · and every day of the last year")
    bx, by, bh, step, bw = 40, 70, 120, (W - 80) / 12, 34
    for i, (k, v) in enumerate(zip(keys, vals)):
        h = max(3, v / top * bh)
        x = bx + i * step + (step - bw) / 2
        body += (f'<rect x="{x:.1f}" y="{by+bh-h:.1f}" width="{bw}" height="{h:.1f}" rx="6" fill="{ACCENT}" '
                 f'style="transform-box:fill-box;transform-origin:bottom;animation:grow .8s ease both;animation-delay:{i*0.06:.2f}s"/>')
        body += f'<text x="{x+bw/2:.1f}" y="{by+bh-h-6:.1f}" fill="{TEXT}" font-size="11" text-anchor="middle">{v}</text>'
        body += f'<text x="{x+bw/2:.1f}" y="{by+bh+18}" fill="{MUTED}" font-size="11" text-anchor="middle">{names[int(k[5:])-1]}</text>'
    # --- heatmap
    start = date.fromisoformat(items[0][0])
    mx = max([v for _, v in items] + [1])
    cell, gap, hx, hy = 12, 3, 36, 250
    levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    for d, v in items:
        dt = date.fromisoformat(d)
        col = (dt - start).days // 7 if start.weekday() == 6 else ((dt - start).days + (start.weekday() + 1) % 7) // 7
        row = (dt.weekday() + 1) % 7
        lvl = 0 if v == 0 else min(4, 1 + int(v / mx * 3.999))
        body += (f'<rect x="{hx + col*(cell+gap)}" y="{hy + row*(cell+gap)}" width="{cell}" height="{cell}" rx="3" '
                 f'fill="{levels[lvl]}" style="animation:fade .5s ease both;animation-delay:{col*0.012:.2f}s"><title>{v} on {d}</title></rect>')
    body += f'<text x="{hx}" y="{hy+7*(cell+gap)+14}" fill="{MUTED}" font-size="11">Less</text>'
    for i, c in enumerate(levels):
        body += f'<rect x="{hx+32+i*(cell+3)}" y="{hy+7*(cell+gap)+4}" width="{cell}" height="{cell}" rx="3" fill="{c}"/>'
    body += f'<text x="{hx+32+5*(cell+3)+4}" y="{hy+7*(cell+gap)+14}" fill="{MUTED}" font-size="11">More</text>'
    style = ("<style>@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
             "@keyframes fade{from{opacity:0}to{opacity:1}}</style>")
    return frame(250 + 7 * (cell + gap) + 36, style + body)


def languages_svg(prof):
    sizes = {}
    for repo in prof["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
    top, rest = ranked[:7], sum(s for _, s in ranked[7:])
    if rest:
        top.append(("Other", rest))
    total = sum(s for _, s in top) or 1
    body = title("Most used languages", "by code size · all owned repos")
    x, y, bw, bh = 32.0, 66, W - 64, 16
    body += f'<clipPath id="r"><rect x="32" y="{y}" width="{bw}" height="{bh}" rx="8"/></clipPath><g clip-path="url(#r)">'
    for i, (n, s) in enumerate(top):
        w = s / total * bw
        body += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bh}" fill="{LANG_COLORS[i]}"/>'
        x += w
    body += "</g>"
    for i, (n, s) in enumerate(top):
        cx = 32 + (i % 4) * ((W - 64) / 4)
        cy = 120 + (i // 4) * 40
        body += f'<circle cx="{cx+6:.0f}" cy="{cy}" r="6" fill="{LANG_COLORS[i]}"/>'
        body += f'<text x="{cx+20:.0f}" y="{cy+5}" fill="{TEXT}" font-size="14" font-weight="600">{esc(n)}</text>'
        body += f'<text x="{cx+20:.0f}" y="{cy+22}" fill="{MUTED}" font-size="12">{s/total*100:.1f}%</text>'
    return frame(210, body)


def main():
    OUT.mkdir(exist_ok=True)
    days, prof = fetch_calendar(), fetch_profile()
    (OUT / "stats.svg").write_text(stats_svg(days, prof))
    (OUT / "activity.svg").write_text(activity_svg(days))
    (OUT / "languages.svg").write_text(languages_svg(prof))
    print(f"ok: {sum(days.values())} contributions across {len(days)} days -> {OUT}")


if __name__ == "__main__":
    main()
