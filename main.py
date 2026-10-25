import re
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEventLoop, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaMetaData, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import curator
import state

BACKGROUND = Path(__file__).resolve().parent / "assets" / "background.jpg"

BUCKET_COLORS = (
    "#66bb6a", "#ef6e6e", "#f0c45c", "#60a5fa", "#a78bfa",
    "#f472b6", "#34d399", "#fb923c", "#94a3b8",
)

HINT = "A/D prev/next · Q/E ±5s · Space play · 1-9/W/S bucket · Ctrl+Z undo · F finish · Ctrl+↑/↓ vol · ? keys"

STYLE = """
QWidget { font-family:"Segoe UI"; }
QMainWindow { background:#0b0f16; }
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
QLabel#details { color:#7e8ba3; font-size:11px; }
QCheckBox { color:#c7d0e0; font-size:11px; }

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
QFrame#warningBar {
    background:#241d10; border:1px solid #5c4a22; border-radius:10px;
}
QLabel#warningTitle { color:#f0c45c; font-size:10px; font-weight:800; }
QLabel#warningText { color:#d9c9a3; font-size:12px; }

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


def human_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def details_text(path, duration_ms=0, resolution=None):
    try:
        st = Path(path).stat()
    except OSError:
        return ""
    parts = []
    if resolution is not None and not resolution.isEmpty():
        parts.append(f"{resolution.width()}x{resolution.height()}")
    parts.append(human_size(st.st_size))
    if duration_ms:
        parts.append(fmt(duration_ms))
    parts.append(datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"))
    return "  ·  ".join(parts)


def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap(str(image_path))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if self._pixmap.isNull():
            painter.fillRect(self.rect(), QColor("#0b0f16"))
            return
        scaled = self._pixmap.scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        painter.drawPixmap(
            (self.width() - scaled.width()) // 2,
            (self.height() - scaled.height()) // 2,
            scaled,
        )
        painter.fillRect(self.rect(), QColor(6, 10, 18, 200))


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
        self.buckets = [dict(b) for b in state.DEFAULT_BUCKETS]
        self.ignored = []
        self.recursive = False
        self.undo_stack = []
        self._state_warned = False

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
        self.details_label = QLabel("")
        self.slider = QSlider(Qt.Horizontal)
        self.time_label = QLabel("00:00 / 00:00")
        self.prev_btn = QPushButton("Prev")
        self.back_btn = QPushButton("-5s")
        self.play_btn = QPushButton("Play")
        self.fwd_btn = QPushButton("+5s")
        self.next_btn = QPushButton("Next")
        self.volume_label = QLabel("Vol")
        self.volume = QSlider(Qt.Horizontal)
        self.badge = QLabel("")
        self.finish_btn = QPushButton("Finish")
        self.recursive_cb = QCheckBox("Subfolders")
        self.buckets_btn = QPushButton("Buckets")
        self.export_btn = QPushButton("Export")
        self.hint_label = QLabel(HINT)
        self.brand_mark = QLabel("VC")
        self.brand_title = QLabel("VidCurator")
        self.brand_sub = QLabel("Video review")
        self.eyebrow = QLabel("NOW REVIEWING")
        self.decision_note = QLabel("Accepted \u2192 accepted/   \u00b7   Declined \u2192 declined/")
        self.footer_note = QLabel("LOCAL ONLY")
        self.warning_bar = QFrame()
        self.warning_title = QLabel("NO FOLDER SELECTED")
        self.warning_text = QLabel("Choose a folder to start reviewing videos.")

        for b in (
            self.open_btn, self.help_btn, self.prev_btn, self.back_btn, self.play_btn,
            self.fwd_btn, self.next_btn, self.finish_btn, self.buckets_btn, self.export_btn,
            self.recursive_cb,
        ):
            b.setFocusPolicy(Qt.NoFocus)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.volume.setFocusPolicy(Qt.NoFocus)

        self.play_btn.setObjectName("playBtn")
        self.finish_btn.setObjectName("finishBtn")
        self.open_btn.setObjectName("openBtn")
        self.help_btn.setObjectName("helpBtn")
        self.file_label.setObjectName("fileLabel")
        self.details_label.setObjectName("details")
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
        self.warning_bar.setObjectName("warningBar")
        self.warning_title.setObjectName("warningTitle")
        self.warning_text.setObjectName("warningText")
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
        self.recursive_cb.setToolTip("Also scan subfolders")
        self.buckets_btn.setToolTip("Edit bucket names and folders")
        self.export_btn.setToolTip("Export decisions as CSV")
        self.buckets_btn.setEnabled(False)
        self.recursive_cb.setEnabled(False)
        self.export_btn.setEnabled(False)
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
        top.addWidget(self.recursive_cb)
        top.addWidget(self.folder_label, 1)
        top.addWidget(self.counts)
        top.addWidget(self.counter)
        top.addWidget(self.buckets_btn)
        top.addWidget(self.export_btn)
        top.addWidget(self.help_btn)

        warning = QHBoxLayout(self.warning_bar)
        warning.setContentsMargins(12, 7, 12, 7)
        warning.setSpacing(10)
        warning.addWidget(self.warning_title)
        warning.addWidget(self.warning_text, 1)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_col.addWidget(self.eyebrow)
        title_col.addWidget(self.file_label)
        title_col.addWidget(self.details_label)
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
        self.decision_actions = QHBoxLayout()
        self.decision_actions.setSpacing(10)
        decision.addLayout(self.decision_actions)
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
        layout.addWidget(self.warning_bar)
        layout.addLayout(stage_header)
        layout.addWidget(video_card, 1)
        layout.addLayout(seek)
        layout.addWidget(transport_card)
        layout.addWidget(decision_card)
        layout.addLayout(bottom)

        central = BackgroundWidget(BACKGROUND)
        central.setObjectName("central")
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setStyleSheet(STYLE)

        self.brand_mark.setAlignment(Qt.AlignCenter)
        self.brand_mark.setFixedSize(36, 36)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setMinimumWidth(108)
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
        self.finish_btn.clicked.connect(self.finish)
        self.buckets_btn.clicked.connect(self.edit_buckets)
        self.export_btn.clicked.connect(self.export_csv)
        self.recursive_cb.toggled.connect(self.toggle_recursive)

        self.slider.sliderPressed.connect(self._drag_start)
        self.slider.sliderReleased.connect(self._drag_end)
        self.slider.sliderMoved.connect(
            lambda ms: self.time_label.setText(f"{fmt(ms)} / {fmt(self.player.duration())}")
        )
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.metaDataChanged.connect(self._update_details)
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.errorOccurred.connect(self._on_error)

        for key, fn in (
            ("W", lambda: self.mark(0)),
            ("S", lambda: self.mark(1)),
            ("Q", lambda: self.seek(-5000)),
            ("E", lambda: self.seek(5000)),
            ("A", lambda: self.step(-1)),
            ("D", lambda: self.step(1)),
            ("Space", self.toggle_play),
            ("Ctrl+Up", lambda: self.volume.setValue(min(100, self.volume.value() + 5))),
            ("Ctrl+Down", lambda: self.volume.setValue(max(0, self.volume.value() - 5))),
            ("Ctrl+Z", self.undo),
            ("F", self.finish),
            ("?", self.show_help),
        ) + tuple((str(i), lambda i=i: self.mark(i)) for i in range(1, 10)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(fn)

        self._build_bucket_buttons()
        self._update_counts()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select video folder")
        if not folder:
            return
        folder = Path(folder)
        data = state.load(folder)
        try:
            files = curator.scan(
                folder,
                data["recursive"],
                [b["folder"] for b in data["buckets"]] + data["ignored"],
            )
        except OSError as e:
            QMessageBox.critical(self, "Folder error", f"Could not read the folder:\n{e}")
            return
        if not files:
            QMessageBox.information(self, "No videos", "No video files found in this folder.")
            return
        self.folder = folder
        self.buckets = data["buckets"]
        self.ignored = data["ignored"]
        self.recursive = data["recursive"]
        self.recursive_cb.blockSignals(True)
        self.recursive_cb.setChecked(self.recursive)
        self.recursive_cb.blockSignals(False)
        self._state_warned = False
        self.marks = {folder / rel: bid for rel, bid in data["marks"].items()}
        self.files = files
        self.index = self._first_unmarked()
        self.undo_stack = []
        self._build_bucket_buttons()
        self.warning_bar.setVisible(False)
        self.folder_label.setText(f"{folder.name} ({len(files)} videos)")
        self.folder_label.setToolTip(str(folder))
        self.finish_btn.setEnabled(True)
        self.buckets_btn.setEnabled(True)
        self.recursive_cb.setEnabled(True)
        self.export_btn.setEnabled(True)
        self._update_counts()
        self.load()

    def _exclude_dirs(self):
        return sorted({b["folder"] for b in self.buckets} | set(self.ignored))

    def _first_unmarked(self):
        return next((i for i, p in enumerate(self.files) if p not in self.marks), 0)

    def _save_state(self):
        if self.folder is None:
            return
        marks = {p.relative_to(self.folder).as_posix(): bid for p, bid in self.marks.items()}
        try:
            state.save(
                self.folder,
                {
                    "buckets": self.buckets,
                    "marks": marks,
                    "ignored": self.ignored,
                    "recursive": self.recursive,
                },
            )
        except OSError as e:
            if not self._state_warned:
                self._state_warned = True
                QMessageBox.warning(
                    self, "Could not save decisions",
                    f"Marks stay in memory for this session.\n{e}",
                )

    def _rescan(self):
        if self.folder is None:
            return
        current = self.files[self.index] if 0 <= self.index < len(self.files) else None
        files = curator.scan(self.folder, self.recursive, self._exclude_dirs())
        self.files = files
        self.index = files.index(current) if current in files else self._first_unmarked()
        self.folder_label.setText(f"{self.folder.name} ({len(files)} videos)")
        self.finish_btn.setEnabled(bool(files))
        self.export_btn.setEnabled(bool(files))
        self._update_counts()
        self.load(autoplay=False)

    def toggle_recursive(self, checked):
        self.recursive = checked
        self._save_state()
        try:
            self._rescan()
        except OSError as e:
            QMessageBox.critical(self, "Folder error", f"Could not read the folder:\n{e}")

    def load(self, autoplay=True):
        if not self.files:
            self.counter.setText("0 / 0")
            self.file_label.setText("")
            self.details_label.setText("")
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
        self._update_details()

    def _update_details(self):
        if not self.files:
            self.details_label.setText("")
            return
        resolution = self.player.metaData().value(QMediaMetaData.Key.Resolution)
        self.details_label.setText(
            details_text(self.files[self.index], self.player.duration(), resolution)
        )

    def _update_badge(self):
        mark = self.marks.get(self.files[self.index]) if self.files else None
        bucket = next((b for b in self.buckets if b["id"] == mark), None)
        if bucket is None:
            self.badge.setText("")
            self.badge.setStyleSheet("")
            return
        color = BUCKET_COLORS[self.buckets.index(bucket) % len(BUCKET_COLORS)]
        self.badge.setStyleSheet(
            f"color:#ffffff; font-weight:700; font-size:11px; padding:6px 14px;"
            f"border-radius:10px; background:{color}; border:1px solid {color};"
        )
        self.badge.setText(bucket["label"].upper())

    def _update_counts(self):
        counts = {b["id"]: 0 for b in self.buckets}
        for path in self.files:
            bid = self.marks.get(path)
            if bid in counts:
                counts[bid] += 1
        remaining = len(self.files) - sum(counts.values())
        parts = [f"Remaining <b>{remaining}</b>"]
        for i, bucket in enumerate(self.buckets):
            color = BUCKET_COLORS[i % len(BUCKET_COLORS)]
            parts.append(
                f"<span style='color:{color}'>{bucket['label']} "
                f"<b>{counts[bucket['id']]}</b></span>"
            )
        self.counts.setText(" &nbsp; ".join(parts))

    def mark(self, index):
        if not self.files or index >= len(self.buckets):
            return
        path = self.files[self.index]
        self.undo_stack.append((path, self.marks.get(path), self.index))
        self.marks[path] = self.buckets[index]["id"]
        self._save_state()
        self._update_counts()
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load()
        else:
            self._update_badge()
            self.file_label.setText("Last video marked. Press F to finish.")

    def undo(self):
        if not self.undo_stack:
            return
        path, previous, index = self.undo_stack.pop()
        if previous is None:
            self.marks.pop(path, None)
        else:
            self.marks[path] = previous
        self.index = index
        self._save_state()
        self._update_counts()
        self.load(autoplay=False)

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
        self._update_details()

    def _on_state(self, playback):
        self.play_btn.setText("Pause" if playback == QMediaPlayer.PlayingState else "Play")

    def _on_error(self, error, message):
        name = self.files[self.index].name if self.files else "video"
        self.file_label.setText(f"Cannot play {name}: {message}")

    def show_help(self):
        QMessageBox.information(self, "Keyboard shortcuts", HINT.replace(" · ", "\n"))

    def _dest_dir(self, path, bucket):
        return self.folder / bucket["folder"] / Path(path).relative_to(self.folder).parent

    def _move_jobs(self, jobs):
        plans = curator.plan_moves(jobs)
        moved, errors = curator.move_planned(plans)
        dests = dict(jobs)
        return moved, [(src, dests[src], msg) for src, msg in errors]

    def _confirm_finish(self, plans, unmarked):
        box = QMessageBox(self)
        box.setWindowTitle("Finish")
        box.setIcon(QMessageBox.Question)
        box.setText(
            f"Move {len(plans)} files into their bucket folders?\n"
            f"{unmarked} unmarked stay in place."
        )
        lines = [
            f"{src.relative_to(self.folder)}  →  {target.relative_to(self.folder)}"
            for src, target in plans[:200]
        ]
        if len(plans) > 200:
            lines.append(f"... and {len(plans) - 200} more")
        box.setDetailedText("\n".join(lines))
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.No)
        return box.exec() == QMessageBox.Yes

    def finish(self):
        if not self.files or self.folder is None:
            return
        by_id = {b["id"]: b for b in self.buckets}
        jobs = [
            (p, self._dest_dir(p, by_id[bid]))
            for p in self.files
            if (bid := self.marks.get(p)) in by_id
        ]
        if not jobs:
            QMessageBox.information(self, "Nothing marked", "Mark at least one video first.")
            return
        plans = curator.plan_moves(jobs)
        if not self._confirm_finish(plans, len(self.files) - len(jobs)):
            return

        self.player.stop()
        self.player.setSource(QUrl())  # release file handle on Windows before moving

        try:
            moved, errors = self._move_jobs(jobs)
            if errors:
                wait(700)  # shortcut: ffmpeg releases the last file handle late, one retry is enough
                retry, errors = self._move_jobs([(p, d) for p, d, _ in errors])
                moved += retry
            for src, _ in jobs:
                if not src.exists():
                    self.marks.pop(src, None)
            self.undo_stack = []
            self._save_state()
            self._rescan()
        except OSError as e:
            QMessageBox.critical(self, "Folder error", f"Could not finish:\n{e}")
            return

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

    def _build_bucket_buttons(self):
        while self.decision_actions.count():
            widget = self.decision_actions.takeAt(0).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        for i, bucket in enumerate(self.buckets):
            color = BUCKET_COLORS[i % len(BUCKET_COLORS)]
            key = "W" if i == 0 else "S" if i == 1 else str(i + 1)
            btn = QPushButton(bucket["label"])
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setMinimumHeight(48)
            btn.setStyleSheet(
                f"background:{color}; border:1px solid {color}; color:#ffffff;"
                "font-size:14px; font-weight:700; padding:12px 22px; border-radius:10px;"
            )
            btn.setToolTip(f"{bucket['label']} ({key})")
            btn.clicked.connect(lambda _=False, i=i: self.mark(i))
            self.decision_actions.addWidget(btn)
        self.decision_note.setText(
            "  ·  ".join(f"{b['label']} → {b['folder']}/" for b in self.buckets)
        )

    def _parse_buckets(self, rows):
        if len(rows) > 9:
            raise ValueError("At most 9 buckets (keys 1-9).")
        buckets, ids, folders = [], set(), set()
        for r, (bucket_id, label, folder) in enumerate(rows):
            label, folder = label.strip(), folder.strip()
            if not label or not folder:
                raise ValueError("Every bucket needs a label and a folder.")
            if any(c in folder for c in "/\\") or folder in (".", ".."):
                raise ValueError(f"Folder names cannot contain slashes: {folder}")
            if folder in folders:
                raise ValueError(f"Folder used twice: {folder}")
            bucket_id = (
                bucket_id
                or re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
                or f"bucket{r + 1}"
            )
            if bucket_id in ids:
                bucket_id = f"{bucket_id}-{r + 1}"
            ids.add(bucket_id)
            folders.add(folder)
            buckets.append({"id": bucket_id, "label": label, "folder": folder})
        if not buckets:
            raise ValueError("Keep at least one bucket.")
        return buckets, folders

    def edit_buckets(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Buckets")
        dlg.resize(460, 320)
        table = QTableWidget(0, 2, dlg)
        table.setHorizontalHeaderLabels(["Label", "Folder"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for b in self.buckets:
            row = table.rowCount()
            table.insertRow(row)
            label = QTableWidgetItem(b["label"])
            label.setData(Qt.UserRole, b["id"])
            table.setItem(row, 0, label)
            table.setItem(row, 1, QTableWidgetItem(b["folder"]))

        add_btn = QPushButton("Add")
        del_btn = QPushButton("Remove")

        def add_row():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem("New"))
            table.setItem(row, 1, QTableWidgetItem(f"bucket{row + 1}"))

        def del_row():
            row = table.currentRow()
            if row < 0:
                return
            bucket_id = table.item(row, 0).data(Qt.UserRole)
            if bucket_id and bucket_id in self.marks.values():
                QMessageBox.warning(
                    dlg, "Bucket in use", "Unmark or move its clips before removing this bucket."
                )
                return
            table.removeRow(row)

        add_btn.clicked.connect(add_row)
        del_btn.clicked.connect(del_row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout = QVBoxLayout(dlg)
        layout.addWidget(table)
        row_layout = QHBoxLayout()
        row_layout.addWidget(add_btn)
        row_layout.addWidget(del_btn)
        row_layout.addStretch(1)
        layout.addLayout(row_layout)
        layout.addWidget(buttons)
        if dlg.exec() != QDialog.Accepted:
            return

        rows = [
            (table.item(r, 0).data(Qt.UserRole), table.item(r, 0).text(), table.item(r, 1).text())
            for r in range(table.rowCount())
        ]
        try:
            buckets, folders = self._parse_buckets(rows)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid bucket", str(e))
            return

        self.ignored = sorted(({b["folder"] for b in self.buckets} - folders) | set(self.ignored))
        self.buckets = buckets
        self._build_bucket_buttons()
        self._update_counts()
        if self.files:
            self._update_badge()
        self._save_state()

    def export_csv(self):
        if not self.files or self.folder is None:
            return
        by_id = {b["id"]: b for b in self.buckets}
        rows = []
        for path in self.files:
            bucket = by_id.get(self.marks.get(path))
            dest = self._dest_dir(path, bucket) / path.name if bucket else ""
            try:
                stamp = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
            except OSError:
                stamp = ""
            rows.append(
                (
                    path.relative_to(self.folder).as_posix(),
                    bucket["label"] if bucket else "",
                    str(dest),
                    stamp,
                )
            )
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Export decisions",
            str(self.folder / "vidcurator-decisions.csv"),
            "CSV (*.csv)",
        )
        if not target:
            return
        try:
            curator.export_csv(target, rows)
        except OSError as e:
            QMessageBox.critical(self, "Export failed", str(e))
            return
        QMessageBox.information(self, "Exported", f"Wrote {len(rows)} rows to {target}")


def main():
    app = QApplication(sys.argv)
    window = VidCurator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
