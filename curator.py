from pathlib import Path
import shutil

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv"}


def scan(folder):
    folder = Path(folder)
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)


def unique_target(dst, name):
    target = Path(dst) / name
    n = 1
    while target.exists():
        target = Path(dst) / f"{Path(name).stem} ({n}){Path(name).suffix}"
        n += 1
    return target


def move_files(paths, dst):
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    moved, errors = [], []
    for src in map(Path, paths):
        try:
            target = unique_target(dst, src.name)
            shutil.move(str(src), str(target))
            moved.append(target)
        except OSError as e:
            errors.append((src, str(e)))
    return moved, errors
