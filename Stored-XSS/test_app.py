import tempfile
import unittest
from pathlib import Path

from app import get_comments, init_db, render_comment_cards, save_comment


class StoredXSSTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "test.sqlite3"
        init_db(self.database)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_comment_is_stored_and_raw_markup_is_present_in_vulnerable_output(self):
        payload = "<script>alert('Stored XSS')</script>"
        save_comment("Mohit Kumar", payload, self.database)
        comments = get_comments(self.database)
        output = render_comment_cards(comments, secure=False)
        self.assertIn(payload, output)

    def test_same_comment_is_encoded_in_secure_output(self):
        payload = "<script>alert('Stored XSS')</script>"
        save_comment("Mohit Kumar", payload, self.database)
        comments = get_comments(self.database)
        output = render_comment_cards(comments, secure=True)
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn(payload, output)

    def test_author_is_escaped_in_both_modes(self):
        save_comment("<b>Mohit</b>", "Hello", self.database)
        comments = get_comments(self.database)
        for secure in (False, True):
            output = render_comment_cards(comments, secure=secure)
            self.assertIn("&lt;b&gt;Mohit&lt;/b&gt;", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
