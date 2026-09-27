#!/usr/bin/env python3
"""Build pluginmaster.json from the latest GitHub release of every plugin repo.

Each repo listed in plugins.json must publish releases with two assets produced
by the Dalamud.NET.Sdk packager:

  latest.zip          the plugin package
  <InternalName>.json the plugin manifest

This script needs only the standard library. Set GITHUB_TOKEN to avoid
anonymous rate limits (GitHub Actions provides it automatically).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_FILE = ROOT / "plugins.json"
OUTPUT_FILE = ROOT / "pluginmaster.json"
API = "https://api.github.com"


def request(url: str, *, raw: bool = False) -> bytes:
    headers = {
        "User-Agent": "AHAKuo-ahadevtools-pluginmaster",
        "Accept": "application/octet-stream" if raw else "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def url_exists(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "AHAKuo-ahadevtools-pluginmaster"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError:
        return False


def latest_release(repo: str) -> dict:
    return json.loads(request(f"{API}/repos/{repo}/releases/latest"))


def default_branch(repo: str) -> str:
    return json.loads(request(f"{API}/repos/{repo}"))["default_branch"]


def build_entry(repo: str) -> dict | None:
    try:
        release = latest_release(repo)
    except urllib.error.HTTPError as e:
        print(f"[{repo}] no release found ({e.code}); skipping", file=sys.stderr)
        return None

    assets = {a["name"]: a for a in release.get("assets", [])}
    zip_asset = assets.get("latest.zip")
    manifest_asset = next(
        (a for name, a in assets.items() if name.endswith(".json") and not name.endswith(".deps.json")),
        None,
    )
    if zip_asset is None or manifest_asset is None:
        print(f"[{repo}] release {release.get('tag_name')} lacks latest.zip or a manifest .json; skipping", file=sys.stderr)
        return None

    manifest = json.loads(request(manifest_asset["url"], raw=True))

    published = release.get("published_at") or release.get("created_at")
    last_update = int(datetime.fromisoformat(published.replace("Z", "+00:00")).timestamp()) if published else 0

    zip_url = zip_asset["browser_download_url"]
    entry = dict(manifest)
    entry.setdefault("RepoUrl", f"https://github.com/{repo}")
    entry["DownloadLinkInstall"] = zip_url
    entry["DownloadLinkUpdate"] = zip_url
    entry["DownloadLinkTesting"] = zip_url
    entry["DownloadCount"] = int(zip_asset.get("download_count", 0))
    entry["LastUpdate"] = last_update
    entry.setdefault("IsHide", False)
    entry.setdefault("IsTestingExclusive", False)

    if not entry.get("IconUrl"):
        branch = default_branch(repo)
        icon = f"https://raw.githubusercontent.com/{repo}/{branch}/images/icon.png"
        if url_exists(icon):
            entry["IconUrl"] = icon

    print(f"[{repo}] {entry.get('Name')} {entry.get('AssemblyVersion')} from {release.get('tag_name')}", file=sys.stderr)
    return entry


def main() -> int:
    repos: list[str] = json.loads(PLUGINS_FILE.read_text(encoding="utf-8"))
    entries = [e for e in (build_entry(r) for r in repos) if e is not None]
    entries.sort(key=lambda e: e.get("InternalName", ""))

    new_text = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    old_text = OUTPUT_FILE.read_text(encoding="utf-8") if OUTPUT_FILE.exists() else None
    if new_text == old_text:
        print("pluginmaster.json unchanged", file=sys.stderr)
        return 0

    OUTPUT_FILE.write_text(new_text, encoding="utf-8")
    print(f"wrote {OUTPUT_FILE} with {len(entries)} plugin(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
