import tempfile
import unittest
from pathlib import Path

import curator


class CuratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def touch(self, *parts):
        path = self.root.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        return path

    def test_scan_top_level_videos_only(self):
        a = self.touch("a.mp4")
        b = self.touch("b.MKV")
        c = self.touch("notes.txt")
        self.touch("sub", "nested.mp4")
        self.assertEqual(curator.scan(self.root), [a, b])

    def test_unique_target_avoids_collisions(self):
        self.assertEqual(curator.unique_target(self.root, "clip.mp4").name, "clip.mp4")
        self.touch("clip.mp4")
        self.assertEqual(curator.unique_target(self.root, "clip.mp4").name, "clip (1).mp4")
        self.touch("clip (1).mp4")
        self.assertEqual(curator.unique_target(self.root, "clip.mp4").name, "clip (2).mp4")
        self.touch("film.final.mp4")
        self.assertEqual(curator.unique_target(self.root, "film.final.mp4").name, "film.final (1).mp4")

    def test_move_files_moves_and_reports_missing(self):
        good = self.touch("good.mp4")
        dup = self.touch("dup.mp4")
        missing = self.root / "gone.mp4"
        dst = self.root / "accepted"
        dst.mkdir()
        (dst / "dup.mp4").write_bytes(b"x")

        moved, errors = curator.move_files([good, dup, missing], dst)

        self.assertEqual(len(moved), 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], missing)
        self.assertFalse(good.exists())
        self.assertFalse(dup.exists())
        self.assertTrue((dst / "good.mp4").exists())
        self.assertTrue((dst / "dup (1).mp4").exists())


if __name__ == "__main__":
    unittest.main()
