#!/usr/bin/env python3
"""Generates the static presentation cards (hero, about, focus) as flat SVGs.

Usage: python3 scripts/cards.py
"""
import base64
import textwrap
from pathlib import Path

from generate import ACCENT, BG, BORDER, CARD, FONT, MUTED, TEXT, W, esc

OUT = Path(__file__).resolve().parent.parent / "assets"
PILL_BG = "#1f2937"


def svg(h, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{FONT}">'
            f'<style>{style}</style><rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>{body}</svg>')


def pill(x, y, label, color=ACCENT):
    w = len(label) * 7.9 + 24
    return (f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{x + w/2:.0f}" y="{y+19}" fill="{TEXT}" font-size="13.5" text-anchor="middle">{esc(label)}</text>'), w + 8


def pills(x, y, labels, color=ACCENT):
    out = ""
    for lab in labels:
        s, w = pill(x, y, lab, color)
        out += s
        x += w
    return out


def brain_image(x, y, height):
    """Stipple brain illustration (assets/brain.png), embedded as a data URI so it works inside <img> SVGs."""
    data = base64.b64encode((OUT / "brain.png").read_bytes()).decode()
    w = height * 537 / 400
    return f'<image x="{x:.0f}" y="{y}" width="{w:.0f}" height="{height}" href="data:image/png;base64,{data}"/>'


def hero():
    body = (f'<text x="40" y="82" fill="{TEXT}" font-size="40" font-weight="700">Milton Angamarca</text>'
            f'<text x="40" y="116" fill="{ACCENT}" font-size="19" font-weight="600">AI systems engineer</text>'
            f'<text x="40" y="144" fill="{MUTED}" font-size="16">Second brain systems · Operations automation · LLM pipelines</text>'
            + pills(40, 166, ["Python", "TypeScript", "Rust", "Meta Tech Provider"]) + brain_image(545, 14, 192))
    return svg(220, body)


def about():
    rows = [
        ("Role", ["AI systems engineer"], None),
        ("Focus", ["Second brain systems: persistent memory and knowledge for AI agents",
                   "Operations automation for critical workflows",
                   "LLM pipelines and agent orchestration"], None),
        ("Daily", None, ["TypeScript", "Python", "Node.js", "Astro"]),
        ("Also writes", None, ["Rust", "Swift", "C#", "Go", "Kotlin", "Dart"]),
        ("Teaches", ["TypeScript, JavaScript and Astro to a university community"], None),
    ]
    body = f'<text x="32" y="44" fill="{TEXT}" font-size="18" font-weight="600">About</text>'
    y = 84
    for n, (label, lines, tags) in enumerate(rows):
        body += f'<text x="32" y="{y+4}" fill="{MUTED}" font-size="14.5">{esc(label)}</text>'
        if lines:
            for i, ln in enumerate(lines):
                body += f'<text x="170" y="{y+4+i*24}" fill="{TEXT}" font-size="15.5">{esc(ln)}</text>'
            y += 24 * len(lines) + 14
        else:
            body += pills(170, y - 13, tags)
            y += 40
        if n < len(rows) - 1:
            body += f'<line x1="32" y1="{y-18}" x2="{W-32}" y2="{y-18}" stroke="{BORDER}" stroke-opacity=".6"/>'
    h = y + 4
    return svg(h, body)


ICONS = {
    "brain": f'<g stroke="{ACCENT}" stroke-width="1.6" fill="none"><line x1="8" y1="10" x2="20" y2="20"/><line x1="20" y1="20" x2="32" y2="9"/><line x1="20" y1="20" x2="20" y2="33"/><line x1="8" y1="10" x2="8" y2="30"/><line x1="32" y1="9" x2="33" y2="29"/></g>'
             f'<g fill="{ACCENT}"><circle cx="8" cy="10" r="3.5"/><circle cx="32" cy="9" r="3.5"/><circle cx="20" cy="20" r="4.5"/><circle cx="20" cy="33" r="3.5"/><circle cx="8" cy="30" r="3"/><circle cx="33" cy="29" r="3"/></g>',
    "bolt": f'<polygon points="23,3 9,22 19,22 16,37 31,16 21,16" fill="{ACCENT}"/>',
    "pipeline": f'<g fill="none" stroke="{ACCENT}" stroke-width="1.8"><rect x="2" y="13" width="9" height="14" rx="2"/><rect x="15.5" y="13" width="9" height="14" rx="2"/><rect x="29" y="13" width="9" height="14" rx="2"/></g>'
                f'<g stroke="{ACCENT}" stroke-width="1.8"><line x1="11" y1="20" x2="15.5" y2="20"/><line x1="24.5" y1="20" x2="29" y2="20"/></g>',
    "chat": f'<path d="M5 8h30a3 3 0 0 1 3 3v15a3 3 0 0 1-3 3H17l-8 7v-7H5a3 3 0 0 1-3-3V11a3 3 0 0 1 3-3z" fill="none" stroke="{ACCENT}" stroke-width="1.8"/>'
            f'<g fill="{ACCENT}"><circle cx="12" cy="18.5" r="2"/><circle cx="20" cy="18.5" r="2"/><circle cx="28" cy="18.5" r="2"/></g>',
}


def focus():
    cards = [
        ("brain", "Second brain systems", "Persistent memory and knowledge layers that give AI agents long-term context."),
        ("bolt", "Operations automation", "AI-driven workflows for business-critical processes, built for reliability and auditability."),
        ("pipeline", "LLM pipelines", "Document and conversation processing, summarization and agent orchestration."),
        ("chat", "Meta Tech Provider experience", "Integrating Meta APIs (such as WhatsApp Business) on behalf of customers, from inside a SaaS product."),
    ]
    body = f'<text x="32" y="44" fill="{TEXT}" font-size="18" font-weight="600">What I work on</text>'
    cw, ch, gap = (W - 64 - 16) / 2, 138, 16
    for i, (icon, name, desc) in enumerate(cards):
        x = 32 + (i % 2) * (cw + gap)
        y = 66 + (i // 2) * (ch + gap)
        body += f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="{ch}" rx="10" fill="{CARD}" stroke="{BORDER}"/>'
        body += f'<rect x="{x:.0f}" y="{y+16}" width="3" height="{ch-32}" rx="1.5" fill="{ACCENT}"/>'
        body += f'<g transform="translate({x+24:.0f},{y+20})">{ICONS[icon]}</g>'
        body += f'<text x="{x+78:.0f}" y="{y+34}" fill="{TEXT}" font-size="16.5" font-weight="600">{esc(name)}</text>'
        for j, ln in enumerate(textwrap.wrap(desc, 38)[:4]):
            body += f'<text x="{x+78:.0f}" y="{y+60+j*20}" fill="{MUTED}" font-size="14">{esc(ln)}</text>'
    h = 66 + 2 * ch + gap + 24
    return svg(h, body)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero())
    (OUT / "about.svg").write_text(about())
    (OUT / "focus.svg").write_text(focus())
    print("ok: hero, about, focus")


if __name__ == "__main__":
    main()
