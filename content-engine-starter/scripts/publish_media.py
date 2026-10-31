#!/usr/bin/env python3
"""Put a run's images and PDFs online so Buffer can fetch them.

  python3 scripts/publish_media.py runs/2026-10-12-some-trend [--media-repo PATH] [--no-wait]

Copies runs/<run>/media/* into your media repo (a public GitHub repo with GitHub
Pages on) at <path_in_repo>/<run>-<code>/, commits ONLY that folder, pushes to
main, then waits until GitHub Pages serves every file. Writes
runs/<run>/media-urls.json.

Settings: config/engine.yaml -> media (repo, base_url, path_in_repo).
The media repo must be cloned next to this repo (default ../<repo name>).
"""
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = yaml.safe_load(open(os.path.join(ROOT, "config", "engine.yaml")))["media"]


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stderr}")
    return r.stdout.strip()


def live(url):
    """True once the file itself is served. Checks a throwaway URL (unique query string), because a
    CDN in front of the site may cache whatever the plain URL returned before the deploy landed, and
    some hosts answer missing files with a 200 HTML page: so the type must not be HTML either."""
    probe = f"{url}?live-check={int(time.time() * 1000)}"
    try:
        with urllib.request.urlopen(urllib.request.Request(probe, method="HEAD"), timeout=20) as r:
            return r.status == 200 and not r.headers.get("Content-Type", "").startswith("text/html")
    except (urllib.error.URLError, TimeoutError):
        return False


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if not cfg.get("repo") or not cfg.get("base_url"):
        sys.exit("Set media.repo and media.base_url in config/engine.yaml first.")
    run_dir = os.path.abspath(args[0])
    name = cfg["repo"].split("/")[-1]
    repo = os.path.abspath(args[args.index("--media-repo") + 1]) if "--media-repo" in args else os.path.join(os.path.dirname(ROOT), name)
    media_dir = os.path.join(run_dir, "media")
    files = sorted(f for f in os.listdir(media_dir) if not f.startswith("."))
    if not files:
        sys.exit(f"No files in {media_dir}")
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"Media repo not found at {repo}. Clone https://github.com/{cfg['repo']} there first.")

    sub = cfg.get("path_in_repo", "social").strip("/")
    # A short random code keeps the folder hard to guess until the post goes out.
    folder = f"{os.path.basename(run_dir)}-{secrets.token_hex(3)}"
    dest = os.path.join(repo, sub, folder)

    if git(repo, "status", "--porcelain"):
        sys.exit(f"Media repo at {repo} has uncommitted changes. Clean it first.")
    git(repo, "fetch", "origin", "main")
    git(repo, "checkout", "main")
    git(repo, "reset", "--hard", "origin/main")
    os.makedirs(dest, exist_ok=True)
    nojekyll = os.path.join(repo, ".nojekyll")
    if not os.path.exists(nojekyll):          # serve files exactly as they are
        open(nojekyll, "w").close()
        git(repo, "add", ".nojekyll")
    for f in files:
        shutil.copy2(os.path.join(media_dir, f), os.path.join(dest, f))
    git(repo, "add", "--", os.path.join(sub, folder))
    staged = git(repo, "diff", "--cached", "--name-only").splitlines()
    outside = [p for p in staged if not (p.startswith(sub + "/") or p == ".nojekyll")]
    if outside:
        sys.exit(f"Refusing to commit: files outside {sub}/ are staged: {outside}")
    git(repo, "commit", "-m", f"media: {os.path.basename(run_dir)}")
    git(repo, "push", "origin", "main")

    base = cfg["base_url"].rstrip("/")
    urls = {f: f"{base}/{sub}/{folder}/{f}" for f in files}
    json.dump(urls, open(os.path.join(run_dir, "media-urls.json"), "w"), indent=2)
    print(json.dumps(urls, indent=2))

    if "--no-wait" in args:
        return
    deadline = time.time() + cfg.get("wait_for_live_seconds", 300)
    pending = set(urls.values())
    while pending and time.time() < deadline:
        pending = {u for u in pending if not live(u)}
        if pending:
            time.sleep(15)
    if pending:
        sys.exit("Not live yet. Is GitHub Pages on for the media repo (Settings > Pages > Deploy from a branch > main / root)? "
                 "If the run can't reach github.io, add *.github.io to the environment's allowed domains or run with --no-wait.\n"
                 + "\n".join(sorted(pending)))
    print("All media live.")


if __name__ == "__main__":
    main()
