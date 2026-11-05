#!/usr/bin/env python3
"""Performance data for the content engine: what Buffer says each published post did, joined to
what the engine knows about it (post type, graphic, topic, Note type), and a report that only calls
a pattern "proven" once there is enough data.

  python3 scripts/performance.py fetch      # pull every sent post + metrics into runs/performance/posts.json
  python3 scripts/performance.py untagged   # posts that still need a topic tag (the performance-review Skill adds them)
  python3 scripts/performance.py report     # writes runs/performance/report-YYYY-MM-DD.md and findings.json

Needs BUFFER_API_KEY (same as scripts/buffer.py). Read-only on Buffer.

How a pattern is judged (thresholds in config/engine.yaml -> performance):
- Results are compared as *relative* performance: a post's impressions divided by the median of the
  same channel's posts around the same time (+/- 45 days), so a growing or shrinking audience doesn't
  look like a format effect.
- Groups are compared on medians (a viral post can't swing them), each group against the rest.
- "not enough data": fewer than min_early posts in the group.
- "early signal": shown for interest, never acted on.
- "proven": the group and the rest each have at least min_group posts, the channel has at least
  min_channel posts in the window, a Mann-Whitney test gives p below max_p, and the same side wins in
  the first and the second half of the window. Only proven patterns are proposed as rules, and a rule
  only applies once the owner confirms it.
"""
import collections
import datetime as dt
import glob
import json
import math
import os
import statistics as st
import sys
from zoneinfo import ZoneInfo

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import buffer  # noqa: E402  (call(), config)

CFG = yaml.safe_load(open(os.path.join(ROOT, "config", "engine.yaml")))
PCFG = {"window_days": 365, "min_early": 5, "min_group": 10, "min_channel": 40, "max_p": 0.05, "timezone": "Europe/London"}
PCFG.update(CFG.get("performance") or {})
OUT = os.path.join(ROOT, "runs", "performance")
TZ = ZoneInfo(PCFG["timezone"])

# The headline measure per channel, and the extra one worth reporting.
MEASURES = {"linkedin": ("impressions", "engagementRate"), "x": ("impressions", "engagementRate"),
            "substack": ("impressions", "freeSubscriptions")}


# ---------- fetch ----------

def engine_index():
    """buffer_id -> what the engine knows: run, post key, graphic, topic themes, Note type."""
    idx = {}
    for res in glob.glob(os.path.join(ROOT, "runs", "**", "buffer-result.json"), recursive=True):
        run_dir = os.path.dirname(res)
        try:
            drafts, results = json.load(open(os.path.join(run_dir, "drafts.json"))), json.load(open(res))
        except (OSError, ValueError):
            continue
        if results and all("index" not in r for r in results):
            if len(results) != len(drafts):
                continue
            results = [dict(r, index=i) for i, r in enumerate(results)]
        themes, title = run_themes(run_dir)
        notes = note_types(run_dir)
        for r in results:
            if "index" not in r or r["index"] >= len(drafts):
                continue
            d = drafts[r["index"]]
            post = d.get("post") or ""
            idx[r["buffer_id"]] = {
                "run": os.path.relpath(run_dir, os.path.join(ROOT, "runs")),
                "post": post,
                "graphic": graphic_kind(d.get("asset"), post),
                "themes": themes,
                "topic_title": title,
                "note_type": notes.get(post),
                "first_comment": bool((d.get("first_comment") or "").strip()),
            }
    return idx


def graphic_kind(asset, post):
    if not asset:
        return "text only"
    if asset.get("type") == "link":
        return "link card"
    if asset.get("type") == "document":
        return "carousel"
    name = os.path.basename(asset.get("url", "")).lower()
    for key, kind in [(".gif", "infographic GIF"), ("infographic", "infographic"), ("sketch", "sketch"),
                      ("notebook", "notebook page"), ("carousel", "carousel")]:
        if key in name:
            return kind
    return "image (other)"


def run_themes(run_dir):
    """The radar themes of the trend a weekly run wrote about (matched on the report title)."""
    rep, rad = os.path.join(run_dir, "report.md"), os.path.join(run_dir, "radar-data.json")
    if not (os.path.exists(rep) and os.path.exists(rad)):
        return [], None
    title = open(rep).readline().lstrip("# ").strip()
    try:
        trends = json.load(open(rad)).get("trends", [])
    except ValueError:
        return [], title
    for t in trends:
        if t.get("name", "").strip().lower() == title.lower():
            return t.get("themes") or [], title
    return [], title


def note_types(run_dir):
    p = os.path.join(run_dir, "notes.json")
    if not os.path.exists(p):
        return {}
    try:
        return {f"note-{n['n']}": n.get("type") for n in json.load(open(p))}
    except (ValueError, KeyError, TypeError):
        return {}


def cmd_fetch():
    org = CFG["buffer"]["organization_id"]
    known = engine_index()
    tags = load_tags()
    rows = []
    for ch, cid in CFG["buffer"]["channels"].items():
        if not cid:
            continue
        after = None
        while True:
            page = f', after: {json.dumps(after)}' if after else ""
            q = ("query { posts(first: 50" + page + ", input: {organizationId: " + json.dumps(org) +
                 ", filter: {channelIds: [" + json.dumps(cid) + "], status: [sent]}}) { pageInfo { hasNextPage endCursor } "
                 "edges { node { id sentAt text assets { __typename } metricsUpdatedAt metrics { type value } } } } }")
            r = buffer.call(q)["posts"]
            for e in r["edges"]:
                p = e["node"]
                if not p.get("sentAt"):
                    continue
                sent = dt.datetime.fromisoformat(p["sentAt"].replace("Z", "+00:00"))
                local = sent.astimezone(TZ)
                eng = known.get(p["id"], {})
                asset = (p.get("assets") or [{}])[0].get("__typename", "") if p.get("assets") else ""
                rows.append({
                    "id": p["id"], "channel": ch, "sent_at": p["sentAt"],
                    "day": local.strftime("%a"), "hour_local": local.hour,
                    "words": len((p.get("text") or "").split()),
                    "first_line": (p.get("text") or "").strip().split("\n")[0][:120],
                    "text": p.get("text") or "",
                    "source": "engine" if eng else "manual",
                    "graphic": eng.get("graphic") or {"ImageAsset": "image", "VideoAsset": "video", "DocumentAsset": "document", "": "text only"}.get(asset, asset),
                    "post": eng.get("post"), "run": eng.get("run"), "note_type": eng.get("note_type"),
                    "themes": tags.get(p["id"], {}).get("themes") or eng.get("themes") or [],
                    "metrics": {m["type"]: m["value"] for m in (p.get("metrics") or [])},
                    "metrics_updated_at": p.get("metricsUpdatedAt"),
                })
            if not r["pageInfo"]["hasNextPage"]:
                break
            after = r["pageInfo"]["endCursor"]
    os.makedirs(OUT, exist_ok=True)
    json.dump({"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "posts": rows},
              open(os.path.join(OUT, "posts.json"), "w"), indent=1, ensure_ascii=False)
    c = collections.Counter(r["channel"] for r in rows)
    print("fetched " + ", ".join(f"{v} {k}" for k, v in c.items()) + f" posts; {sum(r['source'] == 'engine' for r in rows)} matched to engine runs")


def load_tags():
    p = os.path.join(OUT, "tags.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def load_posts():
    p = os.path.join(OUT, "posts.json")
    if not os.path.exists(p):
        sys.exit("Run `python3 scripts/performance.py fetch` first.")
    data = json.load(open(p))
    tags = load_tags()
    for r in data["posts"]:
        if not r["themes"] and r["id"] in tags:
            r["themes"] = tags[r["id"]].get("themes", [])
    return data


def cmd_untagged():
    data = load_posts()
    todo = [r for r in data["posts"] if not r["themes"]]
    for r in todo:
        print(json.dumps({"id": r["id"], "channel": r["channel"], "sent_at": r["sent_at"][:10], "text": r.get("text", r["first_line"])[:400]}, ensure_ascii=False))
    print(f"# {len(todo)} posts without a topic tag", file=sys.stderr)


# ---------- analysis ----------

def relative(rows, key):
    """Each post's value divided by the median of the same channel's posts within +/-45 days."""
    out = {}
    times = [(dt.datetime.fromisoformat(r["sent_at"].replace("Z", "+00:00")), r) for r in rows]
    for t, r in times:
        near = [x["metrics"].get(key, 0) for u, x in times if x is not r and abs((u - t).days) <= 45]
        if len(near) < 5:
            near = [x["metrics"].get(key, 0) for u, x in times if x is not r]
        base = st.median(near) if near else 0
        out[r["id"]] = (r["metrics"].get(key, 0) / base) if base else None
    return out


def mann_whitney_p(a, b):
    """Two-sided Mann-Whitney U p-value (normal approximation with tie correction)."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return 1.0
    allv = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks, i = [0.0] * len(allv), 0
    ties = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2 + 1
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    r1 = sum(rk for rk, (v, g) in zip(ranks, allv) if g == 0)
    u = r1 - n1 * (n1 + 1) / 2
    n = n1 + n2
    sd = math.sqrt(n1 * n2 / 12 * ((n + 1) - ties / (n * (n - 1)))) if n > 1 else 0
    if sd == 0:
        return 1.0
    z = (abs(u - n1 * n2 / 2) - 0.5) / sd
    return math.erfc(z / math.sqrt(2))


def length_bucket(w):
    return "under 90 words" if w < 90 else "90-160 words" if w <= 160 else "160-250 words" if w <= 250 else "250+ words"


def slot(h):
    return "before 10:00" if h < 10 else "10:00-13:00" if h < 13 else "13:00-16:00" if h < 16 else "16:00 or later"


DIMENSIONS = {
    "graphic": lambda r: [r["graphic"]],
    "length": lambda r: [length_bucket(r["words"])],
    "day": lambda r: [r["day"]],
    "time (UK)": lambda r: [slot(r["hour_local"])],
    "topic": lambda r: r["themes"] or ["untagged"],
    "Note type": lambda r: [r["note_type"]] if r.get("note_type") else [],
}


def judge(group, rest, half1, half2):
    n, m = len(group), len(rest)
    if n < PCFG["min_early"]:
        return "not enough data", None
    p = mann_whitney_p(group, rest)
    big_enough = n >= PCFG["min_group"] and m >= PCFG["min_group"]
    up = st.median(group) > st.median(rest)
    consistent = all(len(g) >= 3 and len(o) >= 3 and ((st.median(g) > st.median(o)) == up) for g, o in (half1, half2))
    if big_enough and p < PCFG["max_p"] and consistent:
        return ("proven: better" if up else "proven: worse"), p
    return "early signal", p


def analyse(data):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=PCFG["window_days"])
    findings = []
    for ch, (main, extra) in MEASURES.items():
        rows = [r for r in data["posts"] if r["channel"] == ch and dt.datetime.fromisoformat(r["sent_at"].replace("Z", "+00:00")) >= cutoff]
        if not rows:
            continue
        rel = relative(rows, main)
        rows = [r for r in rows if rel.get(r["id"]) is not None]
        rows.sort(key=lambda r: r["sent_at"])
        mid = rows[len(rows) // 2]["sent_at"] if rows else ""
        enough_channel = len(rows) >= PCFG["min_channel"]
        for dim, fn in DIMENSIONS.items():
            groups = collections.defaultdict(list)
            for r in rows:
                for g in fn(r):
                    groups[g].append(r)
            if len(groups) < 2:
                continue
            for g, members in groups.items():
                if g == "untagged":
                    continue
                ids = {r["id"] for r in members}
                others = [r for r in rows if r["id"] not in ids]
                val = lambda rs: [rel[r["id"]] for r in rs]
                h1 = (val([r for r in members if r["sent_at"] < mid]), val([r for r in others if r["sent_at"] < mid]))
                h2 = (val([r for r in members if r["sent_at"] >= mid]), val([r for r in others if r["sent_at"] >= mid]))
                verdict, p = judge(val(members), val(others), h1, h2)
                if verdict.startswith("proven") and not enough_channel:
                    verdict = "early signal"
                ex = [r["metrics"].get(extra, 0) for r in members]
                findings.append({
                    "channel": ch, "dimension": dim, "group": g, "posts": len(members),
                    "median_relative": round(st.median(val(members)), 2),
                    "median_" + main: st.median(r["metrics"].get(main, 0) for r in members),
                    extra: (sum(ex) if extra == "freeSubscriptions" else round(st.median(ex), 2)),
                    "p": None if p is None else round(p, 3), "verdict": verdict,
                })
    return findings


def cmd_report():
    data = load_posts()
    findings = analyse(data)
    today = dt.date.today().isoformat()
    json.dump({"date": today, "thresholds": PCFG, "findings": findings}, open(os.path.join(OUT, "findings.json"), "w"), indent=1, ensure_ascii=False)
    lines = [f"# Performance report, {today}", "",
             f"Data fetched {data['fetched_at'][:16].replace('T', ' ')} UTC. Window: last {PCFG['window_days']} days. "
             "**Relative** = a post's impressions against the median of the same channel's posts within 45 days of it (1.00 = typical; 1.30 = 30% above).", "",
             f"Rules are only proposed from **proven** patterns: at least {PCFG['min_group']} posts in the group and {PCFG['min_group']} to compare against, "
             f"at least {PCFG['min_channel']} posts on the channel, p < {PCFG['max_p']}, and the same result in both halves of the window. "
             f"Under {PCFG['min_early']} posts a group shows as \"not enough data\"; anything else is an early signal, shown but never acted on.", ""]
    posts = data["posts"]
    for ch, (main, extra) in MEASURES.items():
        rows = [f for f in findings if f["channel"] == ch]
        n = sum(1 for p in posts if p["channel"] == ch)
        if not n:
            continue
        lines += [f"## {ch.capitalize()} ({n} posts)", ""]
        proven = [f for f in rows if f["verdict"].startswith("proven")]
        lines.append("**Proven patterns:** " + ("; ".join(f"{f['dimension']} = {f['group']} ({f['verdict'][8:]}, {f['median_relative']}x, {f['posts']} posts, p={f['p']})" for f in proven) if proven else "none yet") + "")
        lines.append("")
        for dim in DIMENSIONS:
            ds = sorted([f for f in rows if f["dimension"] == dim], key=lambda f: -f["median_relative"])
            if not ds:
                continue
            extra_label = "free subs (total)" if extra == "freeSubscriptions" else "median engagement %"
            lines += [f"### By {dim}", "", f"| {dim} | posts | relative | median {main} | {extra_label} | verdict |", "| --- | --- | --- | --- | --- | --- |"]
            lines += [f"| {f['group']} | {f['posts']} | {f['median_relative']:.2f} | {f['median_' + main]:g} | {f[extra]:g} | {f['verdict']} |" for f in ds]
            lines.append("")
    untagged = sum(1 for p in posts if not p["themes"])
    if untagged:
        lines += [f"_{untagged} posts have no topic tag yet; topics compare only the tagged ones._", ""]
    path = os.path.join(OUT, f"report-{today}.md")
    open(path, "w").write("\n".join(lines))
    print(f"wrote {os.path.relpath(path, ROOT)}: {sum(f['verdict'].startswith('proven') for f in findings)} proven, "
          f"{sum(f['verdict'] == 'early signal' for f in findings)} early signals")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmds = {"fetch": cmd_fetch, "untagged": cmd_untagged, "report": cmd_report}
    if not a or a[0] not in cmds:
        sys.exit(__doc__)
    cmds[a[0]]()
