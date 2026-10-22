import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QApplication, QMessageBox

import main

app = QApplication.instance() or QApplication([])


class UITest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.w = main.VidCurator()
        self.w.folder = self.root
        self.w.files = [self.touch("a.mp4"), self.touch("b.mp4")]
        self.w.marks = {}
        self.w.index = 0
        patch.object(self.w, "load").start()
        self.question = patch.object(QMessageBox, "question", return_value=QMessageBox.Yes).start()
        patch.object(QMessageBox, "information").start()
        patch.object(QMessageBox, "critical").start()
        self.addCleanup(patch.stopall)
        self.addCleanup(self.w.close)
        self.addCleanup(self.tmp.cleanup)

    def touch(self, name):
        path = self.root / name
        path.write_bytes(b"x")
        return path

    def test_shortcuts_do_not_auto_repeat(self):
        shortcuts = self.w.findChildren(QShortcut)
        self.assertTrue(shortcuts)
        for shortcut in shortcuts:
            self.assertFalse(shortcut.autoRepeat(), shortcut.key().toString())

    def test_finish_moves_marked_files(self):
        self.w.marks = {self.w.files[0]: "accepted", self.w.files[1]: "declined"}
        self.w.finish()
        self.assertTrue((self.root / "accepted" / "a.mp4").exists())
        self.assertTrue((self.root / "declined" / "b.mp4").exists())
        self.assertEqual(self.w.files, [])

    def test_finish_retries_locked_file(self):
        path = self.w.files[0]
        self.w.marks = {path: "accepted"}
        original = self.w._move_jobs
        calls = []

        def flaky(jobs):
            calls.append(jobs)
            if len(calls) == 1:
                return [], [(p, d, "locked") for p, d in jobs]
            return original(jobs)

        with patch("main.wait"), patch.object(self.w, "_move_jobs", side_effect=flaky):
            self.w.finish()
        self.assertEqual(len(calls), 2)
        self.assertTrue((self.root / "accepted" / "a.mp4").exists())

    def test_failed_move_keeps_mark(self):
        path = self.w.files[0]
        self.w.marks = {path: "accepted"}
        with patch("main.wait"), patch.object(
            self.w, "_move_jobs", return_value=([], [(path, "accepted", "locked")])
        ):
            self.w.finish()
        self.assertEqual(self.w.marks, {path: "accepted"})
        self.assertTrue(path.exists())

    def test_open_folder_keeps_marks_when_discard_refused(self):
        mark = self.w.files[0]
        self.w.marks = {mark: "accepted"}
        self.question.return_value = QMessageBox.No
        with tempfile.TemporaryDirectory() as other:
            Path(other, "x.mp4").write_bytes(b"x")
            with patch.object(main.QFileDialog, "getExistingDirectory", return_value=other):
                self.w.open_folder()
        self.assertEqual(self.w.marks, {mark: "accepted"})

    def test_close_waits_when_decisions_exist(self):
        self.w.marks = {self.w.files[0]: "accepted"}
        self.w.show()
        self.question.return_value = QMessageBox.No
        self.w.close()
        self.assertTrue(self.w.isVisible())


if __name__ == "__main__":
    unittest.main()
