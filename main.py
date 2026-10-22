import sys
from pathlib import Path

from PySide6.QtCore import QEventLoop, Qt, QTimer, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

import curator

HINT = "A/D prev/next · Q/E ±5s · Space play · W accept · S decline · F finish · Ctrl+↑/↓ vol · ? keys"

STYLE = """
QWidget { font-family:"Segoe UI"; }
QMainWindow { background:#0b0f16; }
QWidget#central {
    background:qlineargradient(x1:0, y1:0, x2:0, y2:1,
                               stop:0 #0b0f16, stop:0.5 #0c1220, stop:1 #0a0e16);
}
QLabel { color:#e7ecf5; }
QLabel#brandMark {
    background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #8b5cf6);
    color:#ffffff; font-size:13px; font-weight:800; border-radius:9px;
}
QLabel#brandTitle { font-size:15px; font-weight:700; color:#f5f7fc; }
QLabel#brandSub { font-size:11px; color:#7e8ba3; }
QLabel#eyebrow { font-size:10px; font-weight:700; color:#7e8ba3; }
QLabel#fileLabel { font-size:20px; font-weight:600; color:#f5f7fc; }
QLabel#folderLabel { color:#9aa8bf; font-size:12px; }
QLabel#counter {
    color:#c7d0e0; font-weight:600; font-size:12px;
    background:#1a2333; border:1px solid #2a3550; border-radius:10px; padding:6px 12px;
}
QLabel#counts {
    color:#aab6c8; font-size:12px; background:#121a29;
    border:1px solid #223049; border-radius:10px; padding:6px 12px;
}
QLabel#hint { color:#78879e; font-size:11px; }
QLabel#decisionNote { color:#66748c; font-size:11px; }
QLabel#footerNote {
    color:#7e8ba3; font-size:10px; font-weight:600;
    background:#121a29; border:1px solid #223049; border-radius:8px; padding:4px 9px;
}
QLabel#timeLabel { color:#93a1b8; font-family:"Consolas"; font-size:12px; }
QLabel#badgeAccepted, QLabel#badgeDeclined {
    color:#ffffff; font-weight:700; font-size:11px;
    padding:6px 14px; border-radius:10px;
}
QLabel#badgeAccepted { background:#0e7a55; border:1px solid #16a374; }
QLabel#badgeDeclined { background:#a62a2a; border:1px solid #d44141; }

QFrame#headerBar, QFrame#decisionBar {
    background:#101827; border:1px solid #1e2a3f; border-radius:14px;
}
QFrame#transportBar {
    background:#0f1624; border:1px solid #1c283c; border-radius:12px;
}
QFrame#videoCard {
    background:#04070b; border:1px solid #24314a; border-radius:12px;
}
QFrame#vDivider { background:#243049; border:none; }

QPushButton {
    background:#192232; border:1px solid #2a3650; border-radius:9px;
    padding:8px 14px; color:#dce4f2; font-size:12px; font-weight:600;
}
QPushButton:hover { background:#223047; border-color:#3a4b6d; }
QPushButton:pressed { background:#131b29; }
QPushButton:disabled { color:#526078; background:#121925; border-color:#1d2839; }
QPushButton#openBtn {
    background:#1b2436; border-color:#39466a; color:#dfe6f5; padding:9px 16px;
}
QPushButton#openBtn:hover { background:#24324a; border-color:#6366f1; }
QPushButton#openBtn:pressed { background:#151d2c; }
QPushButton#helpBtn {
    min-width:32px; max-width:32px; min-height:32px; max-height:32px;
    border-radius:16px; padding:0; color:#aeb9cc; font-weight:700;
}
QPushButton#helpBtn:hover { border-color:#6366f1; color:#ffffff; background:#1d2740; }
QPushButton#acceptBtn {
    background:#0e7a55; border:1px solid #16a374; color:#ffffff;
    font-size:14px; font-weight:700; padding:12px 26px; border-radius:10px;
}
QPushButton#acceptBtn:hover { background:#129368; border-color:#22c58d; }
QPushButton#acceptBtn:pressed { background:#0a6144; }
QPushButton#declineBtn {
    background:#a62a2a; border:1px solid #d44141; color:#ffffff;
    font-size:14px; font-weight:700; padding:12px 26px; border-radius:10px;
}
QPushButton#declineBtn:hover { background:#bf3434; border-color:#ef5555; }
QPushButton#declineBtn:pressed { background:#8a2020; }
QPushButton#finishBtn {
    background:#6366f1; border-color:#8b8df8; color:#ffffff;
    font-size:13px; font-weight:700; padding:12px 22px; border-radius:10px;
}
QPushButton#finishBtn:hover { background:#7679f5; border-color:#a5a8ff; }
QPushButton#finishBtn:pressed { background:#5254d8; }
QPushButton#finishBtn:disabled {
    background:#141b29; border-color:#223049; color:#526078;
}
QPushButton#playBtn {
    min-width:92px; background:#e8edf7; border-color:#e8edf7;
    color:#0b0f16; font-weight:700;
}
QPushButton#playBtn:hover { background:#ffffff; border-color:#ffffff; }
QPushButton#playBtn:pressed { background:#cbd5e5; border-color:#cbd5e5; }

QSlider::groove:horizontal { height:5px; background:#1d2738; border-radius:2px; }
QSlider::sub-page:horizontal {
    background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
    border-radius:2px;
}
QSlider::handle:horizontal {
    width:14px; height:14px; margin:-5px 0;
    border-radius:7px; background:#f5f7fc; border:2px solid #6366f1;
}
QSlider::handle:horizontal:hover { background:#ffffff; border-color:#a5a8ff; }
QSlider::handle:horizontal:disabled { background:#39445a; border-color:#39445a; }
QSlider::sub-page:horizontal:disabled { background:#2a3446; }
QSlider#volumeSlider::groove:horizontal { height:4px; }
QToolTip {
    background:#1a2333; color:#e7ecf5; border:1px solid #2e3d59;
    padding:6px; border-radius:6px;
}
QMessageBox { background:#0f1624; }
QMessageBox QLabel { color:#e7ecf5; }
"""


def fmt(ms):
    s = max(0, ms) // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._refresh()

    def setText(self, text):
        self._full_text = text
        self._refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self):
        elided = self.fontMetrics().elidedText(self._full_text, Qt.ElideRight, max(0, self.width()))
        super().setText(elided)


class VidCurator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VidCurator")
        self.resize(1180, 800)
        self.setMinimumSize(920, 620)

        self.folder = None
        self.files = []
        self.marks = {}
        self.index = 0
        self.dragging = False

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.8)
        self.video = QVideoWidget()
        self.player.setVideoOutput(self.video)

        self.open_btn = QPushButton("Open Folder")
        self.folder_label = ElidedLabel("No folder selected")
        self.counts = QLabel("")
        self.counter = QLabel("0 / 0")
        self.help_btn = QPushButton("?")
        self.file_label = ElidedLabel("Open a folder to begin")
        self.slider = QSlider(Qt.Horizontal)
        self.time_label = QLabel("00:00 / 00:00")
        self.prev_btn = QPushButton("Prev")
        self.back_btn = QPushButton("-5s")
        self.play_btn = QPushButton("Play")
        self.fwd_btn = QPushButton("+5s")
        self.next_btn = QPushButton("Next")
        self.volume_label = QLabel("Vol")
        self.volume = QSlider(Qt.Horizontal)
        self.accept_btn = QPushButton("Accept")
        self.decline_btn = QPushButton("Decline")
        self.badge = QLabel("")
        self.finish_btn = QPushButton("Finish")
        self.hint_label = QLabel(HINT)
        self.brand_mark = QLabel("VC")
        self.brand_title = QLabel("VidCurator")
        self.brand_sub = QLabel("Video review")
        self.eyebrow = QLabel("NOW REVIEWING")
        self.decision_note = QLabel("Accepted \u2192 accepted/   \u00b7   Declined \u2192 declined/")
        self.footer_note = QLabel("LOCAL ONLY")

        for b in (
            self.open_btn, self.help_btn, self.prev_btn, self.back_btn, self.play_btn,
            self.fwd_btn, self.next_btn, self.accept_btn, self.decline_btn, self.finish_btn,
        ):
            b.setFocusPolicy(Qt.NoFocus)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.volume.setFocusPolicy(Qt.NoFocus)

        self.play_btn.setObjectName("playBtn")
        self.accept_btn.setObjectName("acceptBtn")
        self.decline_btn.setObjectName("declineBtn")
        self.finish_btn.setObjectName("finishBtn")
        self.open_btn.setObjectName("openBtn")
        self.help_btn.setObjectName("helpBtn")
        self.file_label.setObjectName("fileLabel")
        self.folder_label.setObjectName("folderLabel")
        self.counter.setObjectName("counter")
        self.counts.setObjectName("counts")
        self.time_label.setObjectName("timeLabel")
        self.hint_label.setObjectName("hint")
        self.brand_mark.setObjectName("brandMark")
        self.brand_title.setObjectName("brandTitle")
        self.brand_sub.setObjectName("brandSub")
        self.eyebrow.setObjectName("eyebrow")
        self.decision_note.setObjectName("decisionNote")
        self.footer_note.setObjectName("footerNote")
        self.volume.setObjectName("volumeSlider")

        self.volume.setRange(0, 100)
        self.volume.setValue(80)
        self.volume.setFixedWidth(110)
        self.volume.setToolTip("Volume (Ctrl+Up / Ctrl+Down)")
        self.volume.valueChanged.connect(lambda v: self.audio.setVolume(v / 100))

        self.open_btn.setToolTip("Choose a folder of videos")
        self.help_btn.setToolTip("Keyboard shortcuts (?)")
        self.prev_btn.setToolTip("Previous video (A)")
        self.back_btn.setToolTip("Back 5 seconds (Q)")
        self.play_btn.setToolTip("Play / pause (Space)")
        self.fwd_btn.setToolTip("Forward 5 seconds (E)")
        self.next_btn.setToolTip("Next video (D)")
        self.accept_btn.setToolTip("Accept and play next (W)")
        self.decline_btn.setToolTip("Decline and play next (S)")
        self.finish_btn.setToolTip("Move marked files now (F)")
        self.finish_btn.setEnabled(False)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        brand_text.addWidget(self.brand_title)
        brand_text.addWidget(self.brand_sub)

        header = QFrame()
        header.setObjectName("headerBar")
        top = QHBoxLayout(header)
        top.setContentsMargins(14, 9, 14, 9)
        top.setSpacing(12)
        top.addWidget(self.brand_mark)
        top.addLayout(brand_text)
        divider = QFrame()
        divider.setObjectName("vDivider")
        divider.setFixedSize(1, 30)
        top.addWidget(divider)
        top.addWidget(self.open_btn)
        top.addWidget(self.folder_label, 1)
        top.addWidget(self.counts)
        top.addWidget(self.counter)
        top.addWidget(self.help_btn)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_col.addWidget(self.eyebrow)
        title_col.addWidget(self.file_label)
        stage_header = QHBoxLayout()
        stage_header.setSpacing(16)
        stage_header.addLayout(title_col, 1)
        stage_header.addWidget(self.badge, 0, Qt.AlignVCenter)

        video_card = QFrame()
        video_card.setObjectName("videoCard")
        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(1, 1, 1, 1)
        video_layout.addWidget(self.video)

        seek = QHBoxLayout()
        seek.setSpacing(14)
        seek.addWidget(self.slider, 1)
        seek.addWidget(self.time_label)

        transport_card = QFrame()
        transport_card.setObjectName("transportBar")
        transport = QHBoxLayout(transport_card)
        transport.setContentsMargins(14, 8, 14, 8)
        transport.setSpacing(8)
        for b in (self.prev_btn, self.back_btn, self.play_btn, self.fwd_btn, self.next_btn):
            transport.addWidget(b)
        transport.addStretch(1)
        transport.addWidget(self.volume_label)
        transport.addWidget(self.volume)

        decision_card = QFrame()
        decision_card.setObjectName("decisionBar")
        decision = QHBoxLayout(decision_card)
        decision.setContentsMargins(14, 12, 14, 12)
        decision.setSpacing(10)
        decision.addWidget(self.accept_btn)
        decision.addWidget(self.decline_btn)
        decision.addStretch(1)
        decision.addWidget(self.decision_note)
        decision.addSpacing(8)
        decision.addWidget(self.finish_btn)

        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        bottom.addWidget(self.hint_label, 1)
        bottom.addWidget(self.footer_note)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 16)
        layout.setSpacing(12)
        layout.addWidget(header)
        layout.addLayout(stage_header)
        layout.addWidget(video_card, 1)
        layout.addLayout(seek)
        layout.addWidget(transport_card)
        layout.addWidget(decision_card)
        layout.addLayout(bottom)

        central = QWidget()
        central.setObjectName("central")
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLE)

        self.brand_mark.setAlignment(Qt.AlignCenter)
        self.brand_mark.setFixedSize(36, 36)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setMinimumWidth(108)
        self.accept_btn.setMinimumSize(140, 48)
        self.decline_btn.setMinimumSize(140, 48)
        self.finish_btn.setMinimumSize(120, 48)
        self.video.setMinimumHeight(300)
        self.slider.setEnabled(False)

        self.open_btn.clicked.connect(self.open_folder)
        self.help_btn.clicked.connect(self.show_help)
        self.prev_btn.clicked.connect(lambda: self.step(-1))
        self.next_btn.clicked.connect(lambda: self.step(1))
        self.back_btn.clicked.connect(lambda: self.seek(-5000))
        self.fwd_btn.clicked.connect(lambda: self.seek(5000))
        self.play_btn.clicked.connect(self.toggle_play)
        self.accept_btn.clicked.connect(lambda: self.mark("accepted"))
        self.decline_btn.clicked.connect(lambda: self.mark("declined"))
        self.finish_btn.clicked.connect(self.finish)

        self.slider.sliderPressed.connect(self._drag_start)
        self.slider.sliderReleased.connect(self._drag_end)
        self.slider.sliderMoved.connect(
            lambda ms: self.time_label.setText(f"{fmt(ms)} / {fmt(self.player.duration())}")
        )
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.errorOccurred.connect(self._on_error)

        for key, fn in (
            ("W", lambda: self.mark("accepted")),
            ("S", lambda: self.mark("declined")),
            ("Q", lambda: self.seek(-5000)),
            ("E", lambda: self.seek(5000)),
            ("A", lambda: self.step(-1)),
            ("D", lambda: self.step(1)),
            ("Space", self.toggle_play),
            ("Ctrl+Up", lambda: self.volume.setValue(min(100, self.volume.value() + 5))),
            ("Ctrl+Down", lambda: self.volume.setValue(max(0, self.volume.value() - 5))),
            ("F", self.finish),
            ("?", self.show_help),
        ):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(fn)

        self._update_counts()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select video folder")
        if not folder:
            return
        if self.marks and QMessageBox.question(
            self, "Discard decisions?",
            f"{len(self.marks)} marked videos have not been moved.\nOpen another folder and discard them?",
        ) != QMessageBox.Yes:
            return
        try:
            files = curator.scan(folder)
        except OSError as e:
            QMessageBox.critical(self, "Folder error", f"Could not read the folder:\n{e}")
            return
        if not files:
            QMessageBox.information(self, "No videos", "No video files found in this folder.")
            return
        self.folder = Path(folder)
        self.files = files
        self.marks = {}
        self.index = 0
        self.folder_label.setText(f"{Path(folder).name} ({len(files)} videos)")
        self.folder_label.setToolTip(folder)
        self.finish_btn.setEnabled(True)
        self._update_counts()
        self.load()

    def load(self, autoplay=True):
        if not self.files:
            self.counter.setText("0 / 0")
            self.file_label.setText("")
            self.badge.setText("")
            self.player.setSource(QUrl())
            return
        self.index = max(0, min(self.index, len(self.files) - 1))
        path = self.files[self.index]
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.setPosition(0)
        if autoplay:
            self.player.play()
        else:
            self.player.pause()
        self.slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        self.slider.setEnabled(False)
        self.counter.setText(f"{self.index + 1} / {len(self.files)}")
        self.file_label.setText(path.name)
        self.file_label.setToolTip(str(path))
        self._update_badge()

    def _update_badge(self):
        mark = self.marks.get(self.files[self.index]) if self.files else None
        name = {"accepted": "badgeAccepted", "declined": "badgeDeclined"}.get(mark, "")
        if self.badge.objectName() != name:
            self.badge.setObjectName(name)
            self.badge.style().unpolish(self.badge)
            self.badge.style().polish(self.badge)
        self.badge.setText(mark.upper() if mark else "")

    def _update_counts(self):
        accepted = sum(1 for p in self.files if self.marks.get(p) == "accepted")
        declined = sum(1 for p in self.files if self.marks.get(p) == "declined")
        remaining = len(self.files) - accepted - declined
        self.counts.setText(
            f"Remaining <b>{remaining}</b> &nbsp; "
            f"<span style='color:#66bb6a'>Accepted <b>{accepted}</b></span> &nbsp; "
            f"<span style='color:#ef6e6e'>Declined <b>{declined}</b></span>"
        )

    def mark(self, status):
        if not self.files:
            return
        self.marks[self.files[self.index]] = status
        self._update_counts()
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load()
        else:
            self._update_badge()
            self.file_label.setText("Last video marked. Press F to finish.")

    def step(self, delta):
        if not self.files:
            return
        target = self.index + delta
        if 0 <= target < len(self.files):
            self.index = target
            self.load()

    def seek(self, delta):
        duration = self.player.duration()
        if duration <= 0:
            return
        self.player.setPosition(max(0, min(self.player.position() + delta, duration)))

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            return
        if self.player.duration() > 0 and self.player.position() >= self.player.duration():
            self.player.setPosition(0)
        self.player.play()

    def _drag_start(self):
        self.dragging = True

    def _drag_end(self):
        self.dragging = False
        self.player.setPosition(self.slider.value())

    def _on_position(self, ms):
        if not self.dragging:
            self.slider.setValue(ms)
        self.time_label.setText(f"{fmt(ms)} / {fmt(self.player.duration())}")

    def _on_duration(self, ms):
        self.slider.setRange(0, max(0, ms))
        self.slider.setEnabled(ms > 0)
        self.time_label.setText(f"{fmt(self.player.position())} / {fmt(ms)}")

    def _on_state(self, state):
        self.play_btn.setText("Pause" if state == QMediaPlayer.PlayingState else "Play")

    def _on_error(self, error, message):
        name = self.files[self.index].name if self.files else "video"
        self.file_label.setText(f"Cannot play {name}: {message}")

    def show_help(self):
        QMessageBox.information(self, "Keyboard shortcuts", HINT.replace(" · ", "\n"))

    def closeEvent(self, event):
        if self.marks and QMessageBox.question(
            self, "Discard decisions?",
            f"{len(self.marks)} marked videos have not been moved.\nQuit and discard them?",
        ) != QMessageBox.Yes:
            event.ignore()
            return
        event.accept()

    def _move_jobs(self, jobs):
        moved, errors = [], []
        for path, dest in jobs:
            m, e = curator.move_files([path], self.folder / dest)
            moved += m
            errors += [(path, dest, msg) for _, msg in e]
        return moved, errors

    def finish(self):
        if not self.files or self.folder is None:
            return
        accepted = [p for p in self.files if self.marks.get(p) == "accepted"]
        declined = [p for p in self.files if self.marks.get(p) == "declined"]
        if not accepted and not declined:
            QMessageBox.information(self, "Nothing marked", "Mark at least one video with W or S first.")
            return
        unmarked = len(self.files) - len(accepted) - len(declined)
        answer = QMessageBox.question(
            self,
            "Finish",
            f"Move {len(accepted)} accepted → accepted/\n"
            f"Move {len(declined)} declined → declined/\n"
            f"{unmarked} unmarked stay in place.\n\nContinue?",
        )
        if answer != QMessageBox.Yes:
            return

        self.player.stop()
        self.player.setSource(QUrl())  # release file handle on Windows before moving

        try:
            jobs = [(p, "accepted") for p in accepted] + [(p, "declined") for p in declined]
            moved, errors = self._move_jobs(jobs)
            if errors:
                wait(700)  # shortcut: ffmpeg releases the last file handle late, one retry is enough
                retry, errors = self._move_jobs([(p, d) for p, d, _ in errors])
                moved += retry
            self.files = curator.scan(self.folder)
        except OSError as e:
            QMessageBox.critical(self, "Folder error", f"Could not finish:\n{e}")
            return

        kept = {p: self.marks[p] for p, _, _ in errors if p in self.marks}
        self.marks = kept
        self.index = 0
        self.load(autoplay=False)
        self._update_counts()
        self.finish_btn.setEnabled(bool(self.files))

        summary = f"Moved {len(moved)} files."
        if errors:
            summary += "\n\nLocked or failed (marks kept — press F again):\n" + "\n".join(
                f"{Path(p).name}: {msg}" for p, _, msg in errors[:10]
            )
            if len(errors) > 10:
                summary += f"\n... and {len(errors) - 10} more"
        QMessageBox.information(self, "Finished", summary)
        if not self.files:
            self.folder_label.setText(f"{self.folder.name} (0 videos left)")
            self.file_label.setText("Folder is empty. Open another folder.")


def main():
    app = QApplication(sys.argv)
    window = VidCurator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
