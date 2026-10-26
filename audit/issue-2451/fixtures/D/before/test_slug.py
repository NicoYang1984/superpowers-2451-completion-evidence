import unittest
from slug import slug
class SlugTest(unittest.TestCase):
    def test_spaces_and_case(self):
        self.assertEqual(slug("  Hello WORLD  "), "hello world")
if __name__ == "__main__": unittest.main()
