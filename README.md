# VidCurator

A local desktop app for quickly reviewing a folder of videos and sorting them into
`accepted/` and `declined/`. Nothing is moved until you press **Finish**.

![VidCurator UI](docs/screenshot.png)

## Features

- Scans top-level video files in a folder (subfolders are ignored).
- Plays videos inline with seek, volume, and play/pause controls.
- Keyboard-first workflow: accept or decline, then jump straight to the next clip.
- Decisions are applied only on **Finish**, with a confirmation prompt.
- Accepted files move to `accepted/`; declined files move to `declined/`; unmarked files stay put.
- Name collisions are handled automatically (`clip (1).mp4`).
- Guards against losing pending decisions when switching folders or closing.
- Fully local: no uploads, accounts, or network calls.
- Dark, keyboard-friendly interface built with PySide6.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux with Qt Multimedia support
- On Windows, PySide6 ships the required multimedia backend.

## Install

```powershell
git clone https://github.com/BagasCaturS/Simple-manual-video-curator.git
cd Simple-manual-video-curator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, call the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe main.py
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Run

```powershell
python main.py
```

## How to use

1. Click **Open Folder** and choose a directory containing videos.
2. Review each clip. Press **W** to accept or **S** to decline; the app advances automatically.
3. Use **A** / **D** to go back or forward, **Q** / **E** to skip 5 seconds,
   **Space** to play or pause, and **Ctrl+Up** / **Ctrl+Down** for volume.
4. Press **F** (or **Finish**) when done.
5. Accepted files move to `<folder>/accepted/`; declined files move to
   `<folder>/declined/`. Unmarked files stay in place.

Moved files disappear from the queue on the next scan. Only files directly inside
the selected folder are listed, so subfolders are not scanned.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `W` | Accept and play next |
| `S` | Decline and play next |
| `A` | Previous video |
| `D` | Next video |
| `Q` | Back 5 seconds |
| `E` | Forward 5 seconds |
| `Space` | Play / pause |
| `Ctrl+Up` / `Ctrl+Down` | Volume up / down |
| `F` | Finish and move marked files |
| `?` | Show shortcuts |

## Supported formats

`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.m4v`, `.wmv`, `.flv`

Actual playback depends on the codecs available through Qt Multimedia on your system.

## Project structure

```
main.py           UI, playback, shortcuts, review and finish flow
curator.py        folder scanning and collision-safe file moves
test_ui.py        UI and finish-flow tests
test_curator.py   file handling tests
requirements.txt  pinned PySide6 packages
```

## Tests

```powershell
python -m unittest -v
```

The UI tests use Qt's offscreen platform, so they do not open a window.

## Notes

- Files are not moved until you confirm **Finish**.
- If a file is still locked by the player, the app waits briefly and retries once.
  Any remaining failures are reported, and their marks are kept so you can press
  **F** again.
- Switching folders or closing with pending decisions asks for confirmation first.

## License

No license file is included. Contact the repository owner before reusing the code.
