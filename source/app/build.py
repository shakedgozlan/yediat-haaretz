"""Builds the quiz: merges every source/questions/*.json into index.html at the repository root.
Run from the repository root:  python3 source/app/build.py
"""
import base64, json, pathlib, shutil, sys
from collections import Counter
from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
QDIR = HERE.parent / "questions"
DIST = HERE.parent.parent  # the repository root is the live site
CATS = {"history", "geography", "tanakh", "leaders", "zionism", "world"}


def load_questions():
    qs, problems = [], []
    for f in sorted(QDIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for q in data:
            q["_file"] = f.name
            qs.append(q)
    ids = Counter(q.get("id") for q in qs)
    for q in qs:
        where = f'{q["_file"]}:{q.get("id")}'
        if ids[q.get("id")] > 1:
            problems.append(f"{where} duplicate id")
        if q.get("cat") not in CATS:
            problems.append(f"{where} bad cat {q.get('cat')}")
        opts = q.get("options") or []
        if len(opts) != 4 or len(set(opts)) != 4:
            problems.append(f"{where} needs 4 distinct options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(opts):
            problems.append(f"{where} bad answer index")
        if not q.get("q"):
            problems.append(f"{where} empty question")
        if not q.get("joke") and not q.get("source"):
            problems.append(f"{where} missing source")
    keep = ["id", "cat", "q", "options", "answer", "explain", "difficulty", "funny", "joke", "source"]
    def keep_value(k, v):
        if k == "answer":
            return True
        return v is not None and v is not False and v != ""
    clean = [{k: q[k] for k in keep if k in q and keep_value(k, q[k])} for q in qs]
    return clean, problems


HEB = "U+0307-0308,U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F"
LAT = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
FONTS = [  # (family, file, unicode-range) - both fonts are SIL Open Font License
    ("Rubik Dirt", "rubik-dirt-hebrew-400-normal.woff2", HEB),
    ("Rubik Dirt", "rubik-dirt-latin-small.woff2", LAT),
    ("Secular One", "secular-one-hebrew-400-normal.woff2", HEB),
    ("Secular One", "secular-one-latin-400-normal.woff2", LAT),
]


def font_css():
    rules = []
    for family, fname, rng in FONTS:
        data = base64.b64encode((HERE / "fonts-v2" / fname).read_bytes()).decode()
        rules.append(
            f"@font-face{{font-family:'{family}';font-style:normal;font-weight:400;font-display:swap;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng};}}"
        )
    return "\n".join(rules)


def topo_uri():
    data = base64.b64encode((HERE / "topo.svg").read_bytes()).decode()
    return "data:image/svg+xml;base64," + data


def draw_icon(size, maskable=False):
    """Dark map tile with contour rings and a red position marker."""
    S = 4  # draw big, then shrink for smooth edges
    W = size * S
    img = Image.new("RGB", (W, W), "#18261A")
    d = ImageDraw.Draw(img)
    cx, cy = W * 0.5, W * 0.52
    k = 0.78 if maskable else 1.0
    for i, r in enumerate([0.42, 0.34, 0.27, 0.20, 0.13]):
        rx, ry = W * r * k * 1.08, W * r * k * 0.9
        ox = W * 0.03 * (i % 2) * k
        d.ellipse([cx - rx + ox, cy - ry, cx + rx + ox, cy + ry], outline="#DCE8C6", width=max(2, int(W * (0.012 if i else 0.016))))
    rr = W * 0.075 * k
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline="#FF5533", width=int(W * 0.018))
    rc = W * 0.03 * k
    d.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill="#FF5533")
    return img.resize((size, size), Image.LANCZOS)


def main():
    qs, problems = load_questions()
    by_cat = Counter(q["cat"] for q in qs)
    print(f"{len(qs)} questions:", dict(by_cat))
    print("funny:", sum(1 for q in qs if q.get("funny")), " jokes:", sum(1 for q in qs if q.get("joke")))
    print("difficulty:", dict(Counter(q.get("difficulty") for q in qs)))
    print("answer positions:", dict(Counter(q["answer"] for q in qs)))
    if problems:
        print("\nPROBLEMS:")
        print("\n".join(problems))
        if "--force" not in sys.argv:
            sys.exit(1)

    DIST.mkdir(exist_ok=True)
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(qs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = tpl.replace("/*__QUESTIONS__*/[]", payload).replace("/*__FONTS__*/", font_css()).replace("/*__TOPO__*/", topo_uri())
    (DIST / "index.html").write_text(html, encoding="utf-8")
    for name in ["manifest.json", "sw.js"]:
        shutil.copy(HERE / name, DIST / name)
    draw_icon(192).save(DIST / "icon-192.png")
    draw_icon(512).save(DIST / "icon-512.png")
    draw_icon(512, maskable=True).save(DIST / "icon-maskable-512.png")
    (DIST / ".nojekyll").write_text("")
    print("\nbuilt", DIST / "index.html", f"({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
