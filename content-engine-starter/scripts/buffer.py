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

drafts.json is written by the content-engine Skill:
  [{"channel": "linkedin", "text": "...",
    "asset": {"type": "image", "url": "https://..."}},
   {"channel": "linkedin", "text": "...",
    "asset": {"type": "document", "url": "https://...pdf",
              "thumbnail_url": "https://...png", "title": "..."}},
   {"channel": "substack", "text": "...", "asset": null}]

Every post is created as a DRAFT (saveToDraft: true). Nothing publishes
until you approve it in Buffer.
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
    if a["type"] == "document":
        return {"document": {"url": a["url"], "thumbnailUrl": a["thumbnail_url"], "title": a["title"]}}
    sys.exit(f"Unknown asset type {a['type']!r}")


def cmd_drafts(path, dry_run=False):
    cfg = yaml.safe_load(open(CONFIG))
    channels = cfg["buffer"]["channels"]
    drafts = json.load(open(path))
    results = []
    for d in drafts:
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
        q = ("mutation { createPost(input: " + gql_literal(inp) + ") { "
             "... on PostActionSuccess { post { id } } ... on MutationError { message } } }")
        if dry_run:
            a_ = d.get("asset") or {}
            print(f"[dry run] {d['channel']}: {len(d['text'])} chars, asset={a_.get('type')} {a_.get('url','')}")
            for u in [a_.get("url"), a_.get("thumbnail_url")]:
                if u and not u.startswith("https://"):
                    sys.exit(f"Asset URL must be public https: {u}")
            if d["channel"] == "x" and len(d["text"]) > 280:
                sys.exit("X post is over 280 characters")
            continue
        res = call(q)["createPost"]
        if "post" in res:
            print(f"draft created: {d['channel']} -> {res['post']['id']}")
            results.append({"channel": d["channel"], "buffer_id": res["post"]["id"]})
        else:
            sys.exit(f"Buffer refused the {d['channel']} draft: {res.get('message')}")
    if not dry_run:
        out = os.path.join(os.path.dirname(path), "buffer-result.json")
        json.dump(results, open(out, "w"), indent=2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in {"orgs", "channels", "drafts"}:
        sys.exit(__doc__)
    if a[0] == "orgs":
        cmd_orgs()
    elif a[0] == "channels":
        cmd_channels(a[1] if len(a) > 1 else None)
    else:
        cmd_drafts(a[1], dry_run="--dry-run" in a)
