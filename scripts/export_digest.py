#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export a compact plain-text digest from the generated HTML report.

The HTML report already contains ONLY the keyword-filtered items (news-item / rss-item).
The raw output/txt snapshots are the unfiltered full hotlists and are deliberately not used.

Fields kept: source, rank, time, title, url. No CSS/JS, no styling, no long prose.
"""
from __future__ import annotations

import argparse
import html as html_lib
import re
from pathlib import Path


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html_lib.unescape(s).replace("\n", " ").strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    args = ap.parse_args()

    text = Path(args.html).read_text(encoding="utf-8")

    # --- filtered hotlist items, grouped by source platform / keyword group ---
    hot_rows: list[tuple[str, str, str, str, str]] = []  # source, rank, time, title, url
    seen_hot: set[str] = set()

    parts = re.split(r'<div class="word-group"[^>]*>', text)
    for part in parts[1:]:
        name_m = re.search(r'<div class="word-name">(.*?)</div>', part, re.S)
        source = clean(name_m.group(1)) if name_m else "未知来源"
        blocks = re.findall(
            r'<div class="news-item[^"]*">(.*?)(?=<div class="news-item|<div class="word-group"|<div class="section-divider"|</body>|$)',
            part,
            re.S,
        )
        for block in blocks:
            link = re.search(
                r'<a href="([^"]+)"[^>]*class="news-link"[^>]*>(.*?)</a>', block, re.S
            )
            if not link:
                continue
            url = html_lib.unescape(link.group(1)).strip()
            title = clean(link.group(2))
            if not title or not url:
                continue
            rank_m = re.search(r'<span class="rank-num[^"]*">\s*(\d+)\s*</span>', block)
            rank = rank_m.group(1) if rank_m else "-"
            time_m = re.search(r'<span class="time-info">(.*?)</span>', block, re.S)
            stamp = clean(time_m.group(1)) if time_m else ""
            key = url or title
            if key in seen_hot:
                continue
            seen_hot.add(key)
            hot_rows.append((source, rank, stamp, title, url))

    # --- filtered RSS items ---
    rss_rows: list[tuple[str, str, str, str]] = []  # source, time, title, url
    seen_rss: set[str] = set()
    rss_blocks = re.findall(
        r'<div class="rss-item">(.*?)(?=<div class="rss-item"|<div class="section-divider"|</body>|$)',
        text,
        re.S,
    )
    for block in rss_blocks:
        link = re.search(
            r'<a href="([^"]+)"[^>]*class="rss-link"[^>]*>(.*?)</a>', block, re.S
        )
        if not link:
            continue
        url = html_lib.unescape(link.group(1)).strip()
        title = clean(link.group(2))
        if not title or not url:
            continue
        authors = re.findall(r'<span class="rss-author"[^>]*>(.*?)</span>', block, re.S)
        source = clean(authors[0]) if authors else "RSS"
        if source in ("NEW", ""):
            source = "RSS"
        time_m = re.search(r'<span class="rss-time">(.*?)</span>', block, re.S)
        stamp = clean(time_m.group(1)) if time_m else ""
        if url in seen_rss:
            continue
        seen_rss.add(url)
        rss_rows.append((source, stamp, title, url))

    lines: list[str] = [
        f"# 全球 AI 热点精简数据 {args.date} {args.time} (Asia/Shanghai)",
        f"# 来源: 已按 AI 关键词过滤的报告 | 热榜 {len(hot_rows)} 条 | RSS {len(rss_rows)} 条",
        "# 字段: 来源 | 排名 | 时间 | 标题 | 链接",
        "",
        "## 热榜（已过滤）",
    ]
    for source, rank, stamp, title, url in hot_rows:
        lines.append(f"[{source}] #{rank} | {stamp} | {title} | {url}")
    lines += ["", "## 国际媒体与官方博客 RSS（已过滤，无排名）"]
    for source, stamp, title, url in rss_rows:
        lines.append(f"[{source}] #- | {stamp} | {title} | {url}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"digest written: {out} | hot={len(hot_rows)} rss={len(rss_rows)} bytes={out.stat().st_size}")


if __name__ == "__main__":
    main()
