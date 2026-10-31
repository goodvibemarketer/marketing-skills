#!/usr/bin/env python3
"""Buffer helper for the content engine.

Authentication, either:
  - In a Claude Code cloud environment on Pro/Max: add the key as an API credential
    for host api.buffer.com (Authorization: Bearer). The proxy adds it; this script
    sends no key and never sees it. Leave BUFFER_API_KEY unset.
  - Anywhere else: set BUFFER_API_KEY in the environment.
Create a key at https://publish.buffer.com/settings/api. Never commit it.

  python3 scripts/buffer.py orgs                      # list organisations
  python3 scripts/buffer.py channels [ORG_ID]         # list channels (ids + service)
  python3 scripts/buffer.py drafts runs/X/drafts.json [--dry-run]
  python3 scripts/buffer.py edits runs/X               # what you changed in Buffer, written to runs/X/edits.json
  python3 scripts/buffer.py edits --all                # every run folder with drafts not yet fully checked

drafts.json is written by the content-engine Skill:
  [{"channel": "linkedin", "text": "...",
    "asset": {"type": "image", "url": "https://..."}},
   {"channel": "linkedin", "text": "...",
    "asset": {"type": "document", "url": "https://...pdf",
              "thumbnail_url": "https://...png", "title": "..."}},
   {"channel": "substack", "text": "...", "asset": null}]

A Substack entry may use {"type": "link", "url": ..., "title": ..., "description": ...}
as its asset: the Note then carries that link as a card (no image).
A LinkedIn or X entry may also carry "first_comment": "...". On LinkedIn Buffer posts
it as the first comment (needs a paid Buffer plan); on X it becomes the reply in a
two-post thread. Substack Notes can't take one: put the link in the Note instead.

Every post is created as a DRAFT (saveToDraft: true). Nothing publishes
until you approve it in Buffer.

`edits` compares each draft the engine sent (drafts.json + buffer-result.json) with the post
as it is in Buffer now: the text, the LinkedIn first comment and the X reply. Each post comes
out as unchanged, edited, deleted (you removed the draft) or pending (still a draft or
scheduled, so it may change again). Once a run's posts are all sent or deleted it's final, and
`--all` skips it. The learn-from-edits Skill turns edits.json into voice rules.

buffer-result.json (next to drafts.json) is written after every draft created.
Re-running the same command skips entries already listed there, so after a
failure you fix the entry and run it again without sending anything twice.
"""
import json
import os
import sys
import urllib.error
import urllib.request

import yaml

API = os.environ.get("BUFFER_API_URL", "https://api.buffer.com")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config", "engine.yaml")


class Enum(str):
    """A GraphQL enum value, written without quotes."""


def gql_literal(v):
    if isinstance(v, Enum):
        return str(v)
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)  # JSON string escaping is valid GraphQL
    if isinstance(v, list):
        return "[" + ", ".join(gql_literal(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {gql_literal(x)}" for k, x in v.items()) + "}"
    raise TypeError(f"can't encode {type(v)}")


def call(query):
    key = os.environ.get("BUFFER_API_KEY")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    # No key: rely on the cloud environment's API credential for api.buffer.com.
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        hint = " (no key sent: add BUFFER_API_KEY, or an API credential for api.buffer.com in the cloud environment)" if e.code in (401, 403) and not key else ""
        sys.exit(f"Buffer API HTTP {e.code}{hint}: {e.read().decode()[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"Can't reach api.buffer.com ({e.reason}). Add an API credential for api.buffer.com, or allow api.buffer.com in the environment's network access.")
    if body.get("errors"):
        sys.exit("Buffer API error: " + json.dumps(body["errors"])[:800])
    return body["data"]


def cmd_orgs():
    data = call("query { account { organizations { id name ownerEmail } } }")
    for o in data["account"]["organizations"]:
        print(f"{o['id']}\t{o['name']}")


def cmd_channels(org_id=None):
    if not org_id:
        org_id = yaml.safe_load(open(CONFIG))["buffer"].get("organization_id")
    if not org_id:
        orgs = call("query { account { organizations { id } } }")["account"]["organizations"]
        org_id = orgs[0]["id"]
        print(f"# organization_id: {org_id}")
    q = f"query {{ channels(input: {{organizationId: {gql_literal(org_id)}}}) {{ id name displayName service isQueuePaused }} }}"
    for c in call(q)["channels"]:
        print(f"{c['service']}\t{c['id']}\t{c.get('displayName') or c['name']}{'  (queue paused)' if c['isQueuePaused'] else ''}")


def asset_input(a):
    if not a:
        return None
    if a["type"] == "image":
        return {"image": {"url": a["url"]}}
    if a["type"] == "link":
        return None  # handled as metadata, see link_metadata()
    if a["type"] == "document":
        return {"document": {"url": a["url"], "thumbnailUrl": a["thumbnail_url"], "title": a["title"]}}
    sys.exit(f"Unknown asset type {a['type']!r}")


def link_metadata(channel, a):
    """Substack Notes take a link card through metadata, not assets."""
    if not a or a.get("type") != "link":
        return None
    if channel != "substack":
        sys.exit(f"link assets are only supported for Substack Notes, not {channel!r}")
    card = {k: a[k] for k in ("url", "title", "description") if a.get(k)}
    return {"substack": {"linkAttachment": card}}


def cmd_drafts(path, dry_run=False):
    cfg = yaml.safe_load(open(CONFIG))
    channels = cfg["buffer"]["channels"]
    drafts = json.load(open(path))
    out = os.path.join(os.path.dirname(path), "buffer-result.json")
    results = []
    if not dry_run and os.path.exists(out):
        results = json.load(open(out))
        if any("index" not in r for r in results):
            sys.exit(f"{out} exists from an older run of this script and doesn't say which entries were sent. "
                     "Check Buffer by hand; refusing to send anything twice.")
    sent = {r["index"] for r in results}
    for n, d in enumerate(drafts):
        if not dry_run and n in sent:
            print(f"already sent, skipping: {d['channel']} (entry {n})")
            continue
        ch = channels.get(d["channel"])
        if not ch and dry_run:
            ch = "<channel id missing>"
            print(f"[dry run] warning: no Buffer channel id for {d['channel']!r} in config/engine.yaml")
        if not ch:
            sys.exit(f"No Buffer channel id for {d['channel']!r} in config/engine.yaml. Run: python3 scripts/buffer.py channels")
        inp = {
            "text": d["text"],
            "channelId": ch,
            "schedulingType": Enum("automatic"),
            "mode": Enum("addToQueue"),
            "saveToDraft": True,
        }
        a = asset_input(d.get("asset"))
        if a:
            inp["assets"] = [a]
        lm = link_metadata(d["channel"], d.get("asset"))
        if lm:
            inp["metadata"] = lm
        fc = (d.get("first_comment") or "").strip()
        if fc and d["channel"] not in ("linkedin", "x"):
            sys.exit(f"first_comment works on LinkedIn and X only, not {d['channel']!r} (on Substack put the link in the Note)")
        if fc and d["channel"] == "linkedin":
            inp["metadata"] = {"linkedin": {"firstComment": fc}}
        if fc and d["channel"] == "x":  # X has no first comment: post a two-post thread, the link as the reply
            inp["metadata"] = {"twitter": {"thread": [{"text": d["text"], **({"assets": [a]} if a else {})}, {"text": fc}]}}
        q = ("mutation { createPost(input: " + gql_literal(inp) + ") { "
             "... on PostActionSuccess { post { id } } ... on MutationError { message } } }")
        if dry_run:
            a_ = d.get("asset") or {}
            print(f"[dry run] {d['channel']}: {len(d['text'])} chars, asset={a_.get('type')} {a_.get('url','')}"
                  + (f", first comment {len(fc)} chars" if fc else ""))
            for u in [a_.get("url"), a_.get("thumbnail_url")]:
                if u and not u.startswith("https://"):
                    sys.exit(f"Asset URL must be public https: {u}")
            if d["channel"] == "x" and len(d["text"]) > 280:
                sys.exit("X post is over 280 characters")
            if d["channel"] == "x" and len(fc) > 280:
                sys.exit("X reply (first_comment) is over 280 characters")
            continue
        res = call(q)["createPost"]
        if "post" in res:
            print(f"draft created: {d['channel']} -> {res['post']['id']}")
            results.append({"index": n, "channel": d["channel"], "post": d.get("post"), "buffer_id": res["post"]["id"]})
            json.dump(results, open(out, "w"), indent=2)  # after every draft, so a re-run never sends it twice
        else:
            sys.exit(f"Buffer refused the {d['channel']} draft: {res.get('message')}")


def call_raw(query):
    """Like call(), but returns (data, errors) instead of stopping on a GraphQL error."""
    key = os.environ.get("BUFFER_API_KEY")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(API, data=json.dumps({"query": query}).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Buffer API HTTP {e.code}: {e.read().decode()[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"Can't reach api.buffer.com ({e.reason}). Add an API credential for api.buffer.com, or allow api.buffer.com in the environment's network access.")
    return body.get("data"), body.get("errors") or []


def _norm(t):
    return "\n".join(line.rstrip() for line in (t or "").strip().splitlines())


def _changes(before, after):
    """Word-level changes, as a short list of {"removed", "added"} pairs."""
    import difflib
    a, b = before.split(" "), after.split(" ")
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append({"removed": " ".join(a[i1:i2]), "added": " ".join(b[j1:j2])})
    return out


def cmd_edits(run_dir):
    drafts_p, result_p = os.path.join(run_dir, "drafts.json"), os.path.join(run_dir, "buffer-result.json")
    if not (os.path.exists(drafts_p) and os.path.exists(result_p)):
        sys.exit(f"{run_dir} has no drafts.json and buffer-result.json")
    drafts, results = json.load(open(drafts_p)), json.load(open(result_p))
    if results and all("index" not in r for r in results):
        # older buffer-result.json files have no index: they list every draft in order
        if len(results) != len(drafts) or any(r["channel"] != d["channel"] for r, d in zip(results, drafts)):
            print(f"{run_dir}: older buffer-result.json that doesn't line up with drafts.json; skipped")
            return None
        results = [dict(r, index=i) for i, r in enumerate(results)]
    posts = []
    for r in results:
        if "index" not in r:
            continue
        d = drafts[r["index"]]
        item = {"index": r["index"], "channel": d["channel"], "post": d.get("post"), "buffer_id": r["buffer_id"]}
        q = ("query { post(input: {id: " + gql_literal(r["buffer_id"]) + "}) { id status sentAt text "
             "metadata { ... on LinkedInPostMetadata { firstComment } ... on TwitterPostMetadata { thread { text } } } } }")
        data, errors = call_raw(q)
        if errors:
            if any((e.get("extensions") or {}).get("code") == "NOT_FOUND" for e in errors):
                item.update(state="deleted", final=True, draft_text=d["text"])
                posts.append(item)
                continue
            sys.exit("Buffer API error: " + json.dumps(errors)[:800])
        p = data["post"]
        meta = p.get("metadata") or {}
        now_comment = meta.get("firstComment")
        if d["channel"] == "x":
            th = meta.get("thread") or []
            now_comment = th[1]["text"] if len(th) > 1 else None
        item.update(status=p["status"], sent_at=p.get("sentAt"), final=p["status"] == "sent")
        edits = {}
        if _norm(p["text"]) != _norm(d["text"]):
            edits["text"] = {"draft": d["text"], "now": p["text"], "changes": _changes(_norm(d["text"]), _norm(p["text"]))}
        fc = (d.get("first_comment") or "").strip()
        if fc and now_comment is not None and _norm(now_comment) != _norm(fc):
            edits["first_comment"] = {"draft": fc, "now": now_comment, "changes": _changes(_norm(fc), _norm(now_comment))}
        item["state"] = "edited" if edits else ("unchanged" if item["final"] else "pending")
        if edits:
            item["edits"] = edits
        posts.append(item)
    import datetime
    out = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "final": all(x["final"] for x in posts), "posts": posts}
    json.dump(out, open(os.path.join(run_dir, "edits.json"), "w"), indent=2, ensure_ascii=False)
    counts = {}
    for x in posts:
        counts[x["state"]] = counts.get(x["state"], 0) + 1
    print(f"{run_dir}: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) + ("" if out["final"] else "  (not final yet)"))
    return out


def cmd_edits_all():
    found = 0
    for dirpath, _, files in sorted(os.walk(os.path.join(ROOT, "runs"))):
        if "buffer-result.json" in files and "drafts.json" in files:
            prev = os.path.join(dirpath, "edits.json")
            if os.path.exists(prev) and json.load(open(prev)).get("final"):
                continue
            cmd_edits(dirpath)
            found += 1
    if not found:
        print("Nothing to check: every run's posts are already final.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in {"orgs", "channels", "drafts", "edits"}:
        sys.exit(__doc__)
    if a[0] == "edits":
        cmd_edits_all() if len(a) < 2 or a[1] == "--all" else cmd_edits(os.path.abspath(a[1]))
    elif a[0] == "orgs":
        cmd_orgs()
    elif a[0] == "channels":
        cmd_channels(a[1] if len(a) > 1 else None)
    else:
        cmd_drafts(a[1], dry_run="--dry-run" in a)
