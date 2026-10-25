import csv
import os
import shutil
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv"}


def scan(folder, recursive=False, exclude=()):
    folder = Path(folder)
    if not recursive:
        return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
    skip = {Path(x).parts[0] for x in exclude if Path(x).parts}
    files = []
    for root, dirs, names in os.walk(folder, followlinks=False):
        if Path(root) == folder:
            dirs[:] = [d for d in dirs if d not in skip]
        files.extend(
            Path(root) / name for name in names if Path(name).suffix.lower() in VIDEO_EXTS
        )
    return sorted(files)


def unique_target(dst, name, reserved=()):
    target = Path(dst) / name
    n = 1
    while target.exists() or target in reserved:
        target = Path(dst) / f"{Path(name).stem} ({n}){Path(name).suffix}"
        n += 1
    return target


def plan_moves(jobs):
    reserved = set()
    plans = []
    for src, dst in jobs:
        target = unique_target(dst, Path(src).name, reserved)
        reserved.add(target)
        plans.append((Path(src), target))
    return plans


def move_planned(plans):
    moved, errors = [], []
    for src, target in plans:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(target))
            moved.append(target)
        except OSError as e:
            errors.append((src, str(e)))
    return moved, errors


def export_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "bucket", "destination", "modified"])
        writer.writerows(rows)
