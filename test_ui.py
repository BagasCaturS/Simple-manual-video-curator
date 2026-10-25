import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QApplication, QMessageBox

import main
import state

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
        patch.object(self.w, "_confirm_finish", return_value=True).start()
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

    def test_human_size(self):
        self.assertEqual(main.human_size(0), "0 B")
        self.assertEqual(main.human_size(1536), "1.5 KB")

    def test_undo_restores_previous_mark(self):
        self.w.mark(0)
        self.assertEqual(self.w.marks[self.w.files[0]], "accepted")
        self.assertEqual(self.w.index, 1)
        self.w.undo()
        self.assertNotIn(self.w.files[0], self.w.marks)
        self.assertEqual(self.w.index, 0)

    def test_open_folder_resumes_at_first_unmarked(self):
        state.save(
            self.root,
            {
                "buckets": state.DEFAULT_BUCKETS,
                "marks": {"a.mp4": "accepted"},
                "ignored": [],
                "recursive": False,
            },
        )
        with patch.object(main.QFileDialog, "getExistingDirectory", return_value=str(self.root)):
            self.w.open_folder()
        self.assertEqual(self.w.index, 1)
        self.assertEqual(self.w.marks[self.root / "a.mp4"], "accepted")

    def test_parse_buckets_keeps_ids_and_rejects_duplicate_folders(self):
        buckets, folders = self.w._parse_buckets([("accepted", "Keep", "keep")])
        self.assertEqual(buckets, [{"id": "accepted", "label": "Keep", "folder": "keep"}])
        self.assertEqual(folders, {"keep"})
        with self.assertRaises(ValueError):
            self.w._parse_buckets([(None, "A", "x"), (None, "B", "x")])

    def test_finish_moves_marked_files(self):
        self.w.marks = {self.w.files[0]: "accepted", self.w.files[1]: "declined"}
        self.w.finish()
        self.assertTrue((self.root / "accepted" / "a.mp4").exists())
        self.assertTrue((self.root / "declined" / "b.mp4").exists())
        self.assertEqual(self.w.files, [])

    def test_finish_moves_to_three_buckets(self):
        third = self.touch("c.mp4")
        self.w.files.append(third)
        self.w.buckets = [
            {"id": "accepted", "label": "Keep", "folder": "keep"},
            {"id": "maybe", "label": "Maybe", "folder": "maybe"},
            {"id": "declined", "label": "Drop", "folder": "drop"},
        ]
        self.w.marks = {self.w.files[0]: "accepted", third: "maybe"}
        self.w.finish()
        self.assertTrue((self.root / "keep" / "a.mp4").exists())
        self.assertTrue((self.root / "maybe" / "c.mp4").exists())

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


if __name__ == "__main__":
    unittest.main()
