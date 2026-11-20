#!/usr/bin/env python3
"""Superfan Spotter: find the Substack subscribers most likely to go paid.

Reads a Substack subscriber export (the CSV from Subscribers > Export, or the
full ZIP from Settings > Exports), takes the email addresses out on load, and
works on anonymous IDs. Writes:

  out/summary.json        what Claude reads: counts, signals, top IDs. No emails.
  out/report.md           the same, for a person to read. No emails.
  out/segments/*.csv      the lists to act on, WITH emails and names, for the
                          user to open. Claude does not read these into the chat.
  out/_private/id_map.csv ID to email, so the user can trace any ID.

Standard library only, so it runs in Claude's code sandbox as well as locally.

  python3 spot.py export.csv --out out           # analyse
  python3 spot.py export.csv --columns           # just show how columns were read
  python3 spot.py export.zip --out out --min-days 30 --today 2026-11-20
"""
import argparse, csv, io, json, os, re, statistics, sys, zipfile
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------- columns ---
# Substack renames export headers from time to time, so columns are found by
# pattern, not by exact name. First match wins. Run with --columns to check.
PATTERNS = {
    "email":     [r"^e-?mail( address)?$", r"^email"],
    "name":      [r"^(full )?name$", r"^first[ _]?name$"],
    "type":      [r"subscription[ _]?type", r"^plan$", r"^type$", r"active[ _]subscription", r"subscription[ _]?status"],
    "stars":     [r"^activity( rating)?$", r"stars", r"engagement"],
    "start":     [r"^start[ _]?date", r"subscri\w*[ _]?date", r"^created", r"date[ _]subscribed", r"^subscribed"],
    "upgrade":   [r"paid[ _]?upgrade", r"first[ _]?paid", r"upgrade[ _]?date"],
    "opens_7":   [r"open\w*.*\b7\s*d", r"open\w*.*7 ?day"],
    "opens_30":  [r"open\w*.*\b30\s*d", r"open\w*.*30 ?day", r"open\w*.*(1|one) ?mo"],
    "opens_6m":  [r"open\w*.*6\s*mo", r"open\w*.*180", r"^emails? opened$", r"^opens$"],
    "received":  [r"received", r"delivered", r"emails? sent"],
    "clicks":    [r"click"],
    "comments":  [r"comment"],
    "shares":    [r"share", r"restack"],
    "views":     [r"(web|post)[ _]?(post[ _]?)?views?", r"page[ _]?views"],
    "last_open": [r"last[ _]?(email[ _]?)?open"],
    "revenue":   [r"revenue", r"amount"],
    "source":    [r"source"],
    "disabled":  [r"email[ _]?disabled", r"unsubscri", r"bounced"],
}
SKIP_FOR = {"opens_6m": ["7", "30"], "source": ["paid"]}

def find_columns(headers):
    found, used = {}, set()
    low = {h: h.strip().lower() for h in headers}
    for key, pats in PATTERNS.items():
        for p in pats:
            for h in headers:
                if h in used: continue
                l = low[h]
                if key in SKIP_FOR and any(s in l for s in SKIP_FOR[key]): continue
                if re.search(p, l):
                    found[key] = h; used.add(h); break
            if key in found: break
    return found

# ------------------------------------------------------------------ values ---
def num(v):
    if v is None: return None
    v = str(v).strip().replace(",", "").replace("$", "").replace("£", "").replace("€", "")
    if v == "" or v.lower() in ("none", "null", "n/a", "-"): return None
    m = re.search(r"-?\d+(\.\d+)?", v)
    return float(m.group()) if m else None

def stars(v):
    if v is None: return None
    s = str(v).strip()
    if "★" in s or "⭐" in s or "*" in s: return float(s.count("★") + s.count("⭐") + s.count("*"))
    n = num(s)
    return None if n is None else max(0.0, min(5.0, n))

DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%d %b %Y", "%B %d, %Y"]
def day(v):
    if not v: return None
    s = re.sub(r"(\.\d+)?(Z|[+-]\d\d:?\d\d)$", "", str(v).strip())
    if not s: return None
    for cand in (s, s[:19], s[:10]):
        for f in DATE_FORMATS:
            try: return datetime.strptime(cand, f).date()
            except ValueError: pass
    return None

def plan(v):
    s = (str(v or "")).strip().lower()
    if not s: return "free"
    if any(k in s for k in ("author", "owner", "admin", "contributor")): return "author"
    if "found" in s: return "founding"
    if "comp" in s: return "comp"
    if "gift" in s: return "gift"
    if any(k in s for k in ("paid", "annual", "month", "yearly", "true", "active")): return "paid"
    if s in ("1", "yes"): return "paid"
    return "free"

def truthy(v):
    return str(v or "").strip().lower() in ("true", "1", "yes", "y")

# ------------------------------------------------------------------ loading ---
def read_csv_text(text):
    text = text.lstrip("﻿")
    return list(csv.DictReader(io.StringIO(text)))

def load(path, today):
    """Return (rows, columns, mode). rows are dicts keyed by our own names."""
    if path.lower().endswith(".zip") or os.path.isdir(path):
        return load_full_export(path, today)
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        raw = list(csv.DictReader(f))
    if not raw: sys.exit("The file has no rows.")
    cols = find_columns(list(raw[0].keys()))
    if "email" not in cols: sys.exit("Couldn't find an email column. Headers were: " + ", ".join(raw[0].keys()))
    rows = []
    for r in raw:
        g = lambda k: r.get(cols[k]) if k in cols else None
        rows.append({
            "email": (g("email") or "").strip().lower(),
            "name": (g("name") or "").strip(),
            "plan": plan(g("type")),
            "stars": stars(g("stars")),
            "start": day(g("start")),
            "upgrade": day(g("upgrade")),
            "opens_7": num(g("opens_7")), "opens_30": num(g("opens_30")), "opens_6m": num(g("opens_6m")),
            "received": num(g("received")), "clicks": num(g("clicks")), "comments": num(g("comments")),
            "shares": num(g("shares")), "views": num(g("views")), "last_open": day(g("last_open")),
            "source": (g("source") or "").strip(), "disabled": truthy(g("disabled")),
        })
    return rows, cols, "dashboard"

def load_full_export(path, today):
    """Full export: email_list*.csv plus posts/<id>.opens.csv and .delivers.csv."""
    files = {}
    if os.path.isdir(path):
        for root, _, names in os.walk(path):
            for n in names:
                if n.endswith(".csv"):
                    with open(os.path.join(root, n), encoding="utf-8-sig", errors="replace") as f: files[os.path.join(root, n)] = f.read()
    else:
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.endswith(".csv"): files[n] = z.read(n).decode("utf-8-sig", errors="replace")
    lists = [k for k in files if re.search(r"email_list|subscribers", os.path.basename(k), re.I)]
    if not lists: sys.exit("Couldn't find the subscriber list (email_list*.csv) in the export.")
    rows, cols, mode = None, None, "full-export"
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tmp_list.csv")
    with open(tmp, "w", encoding="utf-8") as f: f.write(files[lists[0]])
    try: rows, cols, _ = load(tmp, today)
    finally: os.remove(tmp)
    by = {r["email"]: r for r in rows}
    d30, d90 = today - timedelta(days=30), today - timedelta(days=90)
    stats = {e: {"o30": 0, "posts90": set(), "deliv90": set(), "last": None, "o6m": 0} for e in by}
    for name, text in files.items():
        base = os.path.basename(name).lower()
        kind = "opens" if "open" in base else "delivers" if "deliver" in base else None
        if not kind: continue
        post = re.sub(r"\.(opens|delivers)\.csv$", "", base)
        for r in read_csv_text(text):
            c = find_columns(list(r.keys()))
            e = (r.get(c.get("email", ""), "") or "").strip().lower()
            if e not in stats: continue
            ts = None
            for k in r:
                if re.search(r"time|date", k, re.I): ts = day(r[k]); break
            if ts is None: continue
            s = stats[e]
            if kind == "opens":
                if ts >= d30: s["o30"] += 1
                if ts >= today - timedelta(days=182): s["o6m"] += 1
                if ts >= d90: s["posts90"].add(post)
                if s["last"] is None or ts > s["last"]: s["last"] = ts
            elif ts >= d90:
                s["deliv90"].add(post)
    for e, r in by.items():
        s = stats[e]
        r["opens_30"], r["opens_6m"], r["last_open"] = s["o30"], s["o6m"], s["last"]
        r["read_rate_90"] = (len(s["posts90"]) / len(s["deliv90"])) if s["deliv90"] else None
    cols["(opens)"] = "posts/*.opens.csv"
    return rows, cols, mode

# ------------------------------------------------------------------ scoring ---
def percentile_map(values):
    vals = sorted(v for v in values if v is not None)
    if not vals: return lambda v: 0.0
    def p(v):
        if v is None: return 0.0
        below = sum(1 for x in vals if x < v); same = sum(1 for x in vals if x == v)
        return (below + 0.5 * same) / len(vals)
    return p

def score_all(rows, today, min_days):
    p30 = percentile_map([r["opens_30"] for r in rows])
    p6m = percentile_map([r["opens_6m"] for r in rows])
    has_stars = any(r["stars"] is not None for r in rows)
    for r in rows:
        r["tenure"] = (today - r["start"]).days if r["start"] else None
        sig = []
        # 1. Habit: Substack's activity stars (opens and web views, last month).
        if has_stars:
            habit = (r["stars"] or 0) / 5
        else:
            rr = r.get("read_rate_90")
            habit = rr if rr is not None else p6m(r["opens_6m"])
        # 2. Attention beyond opening. Opens are inflated by privacy proxies;
        #    a click, comment or share is a person.
        act = 0.0
        if (r["comments"] or 0) > 0: act += 0.45; sig.append("commented")
        if (r["shares"] or 0) > 0: act += 0.35; sig.append("shared")
        # Corporate email scanners click every link without opening anything:
        # clicks with no opens and no stars aren't a person.
        scanner = (r["clicks"] or 0) > 0 and not (r["opens_6m"] or r["opens_30"]) and not (r["stars"] or 0)
        if scanner: sig.append("clicks but never opens (likely a link scanner)")
        elif (r["clicks"] or 0) > 0: act += 0.25 if (r["clicks"] or 0) < 3 else 0.35; sig.append("clicks links")
        if (r["views"] or 0) > 0: act += 0.15; sig.append("reads on the web")
        act = min(act, 1.0)
        # 3. Recent opens relative to the rest of the list.
        recent = p30(r["opens_30"]) if r["opens_30"] is not None else 0.0
        # 4. Tenure: a reader who has stayed is past the honeymoon.
        ten = 0.0 if r["tenure"] is None else min(r["tenure"] / max(min_days * 3, 1), 1.0)
        # 5. Recency of last open.
        rec = 0.0
        if r["last_open"]:
            gap = (today - r["last_open"]).days
            rec = 1.0 if gap <= 14 else 0.5 if gap <= 30 else 0.0
        r["score"] = round(100 * (0.45 * habit + 0.25 * act + 0.15 * recent + 0.10 * ten + 0.05 * rec))
        if has_stars and r["stars"] is not None: sig.insert(0, f"{int(r['stars'])}★")
        if r.get("read_rate_90") is not None: sig.append(f"opened {round(r['read_rate_90'] * 100)}% of posts in 90 days")
        if r["opens_30"]: sig.append(f"{int(r['opens_30'])} opens in 30 days")
        if r["tenure"] is not None: sig.append(f"subscribed {r['tenure']} days")
        r["signals"] = sig
    return has_stars

def segment(rows, has_stars, min_days):
    for r in rows:
        paid = r["plan"] in ("paid", "founding")
        hot = (r["stars"] or 0) >= 4 if has_stars else r["score"] >= 60
        cold = ((r["stars"] or 0) <= 1 if has_stars else r["score"] < 20) and not (r["opens_30"] or 0)
        if r["plan"] == "author": seg = "author"
        elif r["disabled"]: seg = "unsubscribed"
        elif r["plan"] == "comp": seg = "comp"
        elif paid and hot: seg = "paid_superfans"
        elif paid and cold: seg = "paid_at_risk"
        elif paid: seg = "paid_other"
        elif hot and (r["tenure"] is None or r["tenure"] >= min_days): seg = "ready_to_upgrade"
        elif hot: seg = "rising"
        else: seg = "free_other"
        r["segment"] = seg

SEGMENTS = {
    "ready_to_upgrade": "Free readers with the reading habit of a paying subscriber, past their first month. Your best upgrade prospects.",
    "rising": "New free readers who are already highly active. Too early to sell; welcome them properly.",
    "paid_superfans": "Paying readers who read everything. Ask for a testimonial, a referral or a reply.",
    "paid_at_risk": "Paying readers who have stopped opening. Check in before their renewal.",
}

# ------------------------------------------------------------------- output ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export"); ap.add_argument("--out", default="superfan-spotter")
    ap.add_argument("--min-days", type=int, default=30, help="days subscribed before an upgrade ask (default 30)")
    ap.add_argument("--today", help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--columns", action="store_true", help="only show how the columns were read")
    a = ap.parse_args()
    today = datetime.strptime(a.today, "%Y-%m-%d").date() if a.today else date.today()
    rows, cols, mode = load(a.export, today)
    rows = [r for r in rows if r["email"]]

    if a.columns:
        print(json.dumps({"mode": mode, "rows": len(rows), "columns_found": cols,
                          "missing": [k for k in ("type", "stars", "start", "opens_30", "clicks", "comments") if k not in cols and not (mode == "full-export" and k.startswith("opens"))]}, indent=2))
        return

    # Emails out: everything from here works on anonymous IDs.
    rows.sort(key=lambda r: r["email"])
    for i, r in enumerate(rows, 1): r["id"] = f"S{i:05d}"
    has_stars = score_all(rows, today, a.min_days)
    segment(rows, has_stars, a.min_days)

    os.makedirs(os.path.join(a.out, "segments"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "_private"), exist_ok=True)
    with open(os.path.join(a.out, "_private", "id_map.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "email", "name"])
        for r in rows: w.writerow([r["id"], r["email"], r["name"]])
    for seg in SEGMENTS:
        members = sorted([r for r in rows if r["segment"] == seg], key=lambda r: -r["score"])
        with open(os.path.join(a.out, "segments", f"{seg}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "email", "name", "first_name", "plan", "stars", "score", "subscribed_days", "signals"])
            for r in members:
                first = r["name"].split()[0] if r["name"] else ""
                w.writerow([r["id"], r["email"], r["name"], first, r["plan"], "" if r["stars"] is None else int(r["stars"]), r["score"], r["tenure"] if r["tenure"] is not None else "", "; ".join(r["signals"])])

    free = [r for r in rows if r["plan"] in ("free", "gift") and not r["disabled"]]
    paid = [r for r in rows if r["plan"] in ("paid", "founding") and not r["disabled"]]
    def dist(group):
        d = {}
        for r in group:
            k = "unknown" if r["stars"] is None else str(int(r["stars"]))
            d[k] = d.get(k, 0) + 1
        return dict(sorted(d.items()))
    paid_med = statistics.median([r["stars"] for r in paid if r["stars"] is not None]) if any(r["stars"] is not None for r in paid) else None
    counts = {s: sum(1 for r in rows if r["segment"] == s) for s in list(SEGMENTS) + ["paid_other", "free_other", "comp", "unsubscribed", "author"]}
    top = sorted([r for r in rows if r["segment"] == "ready_to_upgrade"], key=lambda r: -r["score"])[: a.top]
    signal_share = {}
    for name in ("commented", "shared", "clicks links", "reads on the web"):
        signal_share[name] = sum(1 for r in top if name in r["signals"])
    summary = {
        "as_of": today.isoformat(), "mode": mode, "min_days": a.min_days,
        "subscribers": len(rows), "free": len(free), "paid": len(paid),
        "paid_share": round(len(paid) / max(len(free) + len(paid), 1), 4),
        "stars_available": has_stars,
        "stars_free": dist(free), "stars_paid": dist(paid), "paid_median_stars": paid_med,
        "segments": counts, "segment_meaning": SEGMENTS,
        "names_on_file": {sg: sum(1 for r in rows if r["segment"] == sg and r["name"]) for sg in SEGMENTS},
        "segment_filter": {
            "ready_to_upgrade": f"Free subscribers, activity {'4-5 stars' if has_stars else 'high'}, signed up before {(today - timedelta(days=a.min_days)).isoformat()}",
            "rising": f"Free subscribers, activity {'4-5 stars' if has_stars else 'high'}, signed up on or after {(today - timedelta(days=a.min_days)).isoformat()}",
            "paid_superfans": "Paid subscribers, activity 4-5 stars",
            "paid_at_risk": "Paid subscribers, activity 0-1 stars",
        },
        "top_ready": [{"id": r["id"], "score": r["score"], "plan": r["plan"], "signals": r["signals"]} for r in top],
        "top_ready_signal_counts": signal_share,
        "suspected_link_scanners": sum(1 for r in rows if any("link scanner" in x for x in r["signals"])),
        "imported_share": round(sum(1 for r in rows if r["source"].lower() == "import") / max(len(rows), 1), 4),
        "columns_used": cols,
        "files": {"segments": os.path.join(a.out, "segments"), "id_map": os.path.join(a.out, "_private", "id_map.csv")},
    }
    with open(os.path.join(a.out, "summary.json"), "w") as f: json.dump(summary, f, indent=2, default=str)

    L = [f"# Superfan Spotter report ({today.isoformat()})", "",
         f"{len(rows)} subscribers: {len(free)} free, {len(paid)} paid ({summary['paid_share']:.1%} paid).", ""]
    if has_stars:
        L += ["## Activity stars", "", "| Stars | Free | Paid |", "| --- | --- | --- |"]
        for k in sorted(set(summary["stars_free"]) | set(summary["stars_paid"])):
            L.append(f"| {k} | {summary['stars_free'].get(k, 0)} | {summary['stars_paid'].get(k, 0)} |")
        L.append("")
    L += ["## Segments", "", "| Segment | People | What it means |", "| --- | --- | --- |"]
    for s, meaning in SEGMENTS.items(): L.append(f"| {s.replace('_', ' ')} | {counts[s]} | {meaning} |")
    L += ["", "## Rebuild these in Substack (Subscribers, then Segments)", ""]
    for s, f in summary["segment_filter"].items():
        if counts[s]: L.append(f"- **{s.replace('_', ' ')}** ({counts[s]}, {summary['names_on_file'][s]} with a name on file): {f}")
    L += ["", f"## Top {len(top)} upgrade prospects (anonymous IDs)", "", "| ID | Score | Signals |", "| --- | --- | --- |"]
    for r in top: L.append(f"| {r['id']} | {r['score']} | {', '.join(r['signals'])} |")
    if summary["suspected_link_scanners"]:
        L += ["", f"{summary['suspected_link_scanners']} addresses click links but have never opened an email: most likely company email scanners, so their clicks aren't counted."]
    if summary["imported_share"] > 0.5:
        L += ["", f"{summary['imported_share']:.0%} of the list was imported, so 'subscribed N days' counts from the import date, not when they first signed up."]
    L += ["", "Emails and names for each segment are in `segments/`. IDs map back to emails in `_private/id_map.csv`."]
    with open(os.path.join(a.out, "report.md"), "w") as f: f.write("\n".join(L) + "\n")
    print(json.dumps({k: summary[k] for k in ("subscribers", "free", "paid", "segments", "stars_available")}, indent=2))
    print(f"Wrote {a.out}/summary.json, report.md and segments/*.csv")

if __name__ == "__main__":
    main()
