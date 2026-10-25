import tempfile
import unittest
from pathlib import Path

import state


class StateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_roundtrip(self):
        state.save(
            self.root,
            {
                "buckets": [{"id": "keep", "label": "Keep", "folder": "keep"}],
                "marks": {"sub/a.mp4": "keep"},
                "ignored": ["old"],
                "recursive": True,
            },
        )
        data = state.load(self.root)
        self.assertEqual(data["marks"], {"sub/a.mp4": "keep"})
        self.assertEqual(data["buckets"], [{"id": "keep", "label": "Keep", "folder": "keep"}])
        self.assertEqual(data["ignored"], ["old"])
        self.assertTrue(data["recursive"])

    def test_corrupt_file_uses_defaults(self):
        (self.root / state.SIDECAR).write_text("{not json", encoding="utf-8")
        data = state.load(self.root)
        self.assertEqual(data["buckets"], state.DEFAULT_BUCKETS)
        self.assertEqual(data["marks"], {})

    def test_unknown_bucket_mark_dropped(self):
        state.save(
            self.root,
            {
                "buckets": state.DEFAULT_BUCKETS,
                "marks": {"a.mp4": "ghost"},
                "ignored": [],
                "recursive": False,
            },
        )
        self.assertEqual(state.load(self.root)["marks"], {})


if __name__ == "__main__":
    unittest.main()
