#!/usr/bin/env python3
"""Curly quotes in prose: check (default) or fix (--fix) the site's HTML pages.

Prose is text outside tags, comments, attribute values, script, style, code,
pre, kbd, samp, var, tt and textarea. Apostrophes become ’ and quote pairs
become “ ” or ‘ ’. Everything else on the page is left byte for byte.

  python3 tools/quotes.py            # count straight quotes in prose; exit 1 if any
  python3 tools/quotes.py --fix      # curl them in place, then count again
  python3 tools/quotes.py --list     # show each straight quote with its context
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"script", "style", "code", "pre", "kbd", "samp", "var", "tt", "textarea", "template"}
RAW = {"script", "style", "textarea"}
INLINE = {"a", "abbr", "b", "bdi", "bdo", "cite", "data", "dfn", "em", "i", "mark", "q", "s",
          "small", "span", "strong", "sub", "sup", "time", "u", "wbr"}
ENTITY = re.compile(r"&(#\d+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
ELISIONS = ("tis", "twas", "em ", "n'", "cause", "til ", "round")
OPENERS = set(" \t\n\r\u00a0([{\u2014\u2013/-\u201c\u2018")


def stream(src):
    """Return the prose as a list of (char, start, end) source spans, in order."""
    out, i, n, stack = [], 0, len(src), []
    while i < n:
        if src.startswith("<!--", i):
            j = src.find("-->", i)
            i = n if j < 0 else j + 3
            continue
        m = re.match(r"<(/?)([A-Za-z][A-Za-z0-9-]*)", src[i:])
        if src[i] == "<" and (m or src.startswith("<!", i)):
            j, q = i + 1, None
            while j < n:  # find the tag's end, skipping quoted attribute values
                c = src[j]
                if q:
                    if c == q:
                        q = None
                elif c in "\"'":
                    q = c
                elif c == ">":
                    break
                j += 1
            end = j + 1
            if m:
                closing, name = m.group(1) == "/", m.group(2).lower()
                if name not in INLINE:
                    out.append((" ", i, i))  # a block boundary reads as a space
                if closing:
                    if name in stack:
                        while stack and stack.pop() != name:
                            pass
                elif name in SKIP and not src[i:end].endswith("/>"):
                    if name in RAW:
                        k = src.lower().find("</" + name, end)
                        end = n if k < 0 else k
                    else:
                        stack.append(name)
            i = end
            continue
        j = src.find("<", i)
        j = n if j < 0 else j
        if not any(s in SKIP for s in stack):
            k = i
            while k < j:
                em = ENTITY.match(src, k) if src[k] == "&" else None
                if em:
                    out.append((html.unescape(em.group(0)), k, em.end()))
                    k = em.end()
                else:
                    out.append((src[k], k, k + 1))
                    k += 1
        i = j
    return out


def curl(chars):
    """Yield (start, end, replacement) for each straight quote in the prose stream."""
    text = "".join(c[0][:1] for c in chars)
    last_double = "\u201d"
    for idx, (c, s, e) in enumerate(chars):
        if c in "\u201c\u201d":
            last_double = c
        if c not in "'\"":
            continue
        prev = text[idx - 1] if idx else " "
        nxt = text[idx + 1] if idx + 1 < len(text) else " "
        rest = text[idx + 1: idx + 7].lower()
        if c == '"':
            if prev in OPENERS:
                r = "“"
            elif not nxt.isalnum():
                r = "”"
            else:  # words on both sides, as across </span><span>: pair with the last one
                r = "”" if last_double == "“" else "“"
            last_double = r
            yield s, e, r
        elif prev in OPENERS:
            if nxt.isdigit() or rest.startswith(ELISIONS):
                yield s, e, "\u2019"
            else:
                yield s, e, "\u2018"
        else:
            yield s, e, "\u2019"


def pages():
    return sorted(p for p in ROOT.glob("*.html"))


def main(argv):
    fix, show = "--fix" in argv, "--list" in argv
    total = 0
    for p in pages():
        src = p.read_text(encoding="utf-8")
        edits = list(curl(stream(src)))
        before = len(edits)
        if show:
            for s, e, r in edits:
                line = src.count("\n", 0, s) + 1
                ctx = src[max(0, s - 40): e + 40].replace("\n", " ")
                print(f"{p.name}:{line}: {r} | {ctx}")
        if fix and edits:
            for s, e, r in sorted(edits, reverse=True):
                src = src[:s] + r + src[e:]
            p.write_text(src, encoding="utf-8")
        after = len(list(curl(stream(src)))) if fix else before
        total += after
        print(f"{p.name}: {before} straight" + (f", {after} after" if fix else ""))
    print(("QUOTES GREEN" if total == 0 else f"QUOTES RED: {total} straight quotes in prose"))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
