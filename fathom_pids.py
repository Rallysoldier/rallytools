#!/usr/bin/env python
# pip install psutil
import psutil
from datetime import datetime
from typing import Optional

def get_local_tz(preferred_key: Optional[str] = "America/Chicago"):
    """Return a tzinfo: try ZoneInfo(preferred_key), else system local tz."""
    try:
        from zoneinfo import ZoneInfo
        if preferred_key:
            return ZoneInfo(preferred_key)
        # fall through to local if no key given
    except Exception:
        pass
    # System local tz (works on Windows without tzdata)
    return datetime.now().astimezone().tzinfo

LOCAL_TZ = get_local_tz("America/Chicago")

def human_delta(td):
    secs = int(td.total_seconds())
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:   parts.append(f"{days}d")
    if hours:  parts.append(f"{hours}h")
    if minutes:parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)

now = datetime.now(LOCAL_TZ)
rows = []

for p in psutil.process_iter(["pid", "name", "exe", "create_time"]):
    try:
        name = (p.info["name"] or "")
        if not name.lower().startswith("fathom"):
            continue
        started = datetime.fromtimestamp(p.info["create_time"], LOCAL_TZ)
        rows.append({
            "pid": p.info["pid"],
            "name": name,
            "exe": p.info.get("exe") or "",
            "started_local": started.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "started_iso": started.isoformat(),
            "uptime": human_delta(now - started),
        })
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

if not rows:
    print("No Fathom process found.")
else:
    for r in rows:
        print(
            f"PID {r['pid']:>6} | {r['name']:<12} | started: {r['started_local']} "
            f"({r['started_iso']}) | uptime: {r['uptime']}\n"
            f"  exe: {r['exe']}\n"
        )


'''
SIMPLE VERSION:

import psutil, time
for p in psutil.process_iter(['pid','name','exe','create_time']):
    try:
        if (p.info['name'] or '').lower().startswith('fathom'):
            print(p.info)
    except psutil.NoSuchProcess:
        pass
'''