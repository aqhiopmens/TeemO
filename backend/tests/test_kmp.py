import unittest

from algorithms.kmp import kmp_search, _compute_lps


class TestKmpSearch(unittest.TestCase):
    def test_empty_pattern_returns_zero(self):
        self.assertEqual(kmp_search('anything', ''), 0)

    def test_pattern_not_found_returns_minus_one(self):
        self.assertEqual(kmp_search('hello world', 'xyz'), -1)

    def test_match_at_start(self):
        self.assertEqual(kmp_search('abcdef', 'abc'), 0)

    def test_match_in_middle(self):
        self.assertEqual(kmp_search('xxabcyy', 'abc'), 2)

    def test_match_at_end(self):
        self.assertEqual(kmp_search('xxxabc', 'abc'), 3)

    def test_pattern_equal_to_text(self):
        self.assertEqual(kmp_search('abc', 'abc'), 0)

    def test_pattern_longer_than_text_returns_minus_one(self):
        self.assertEqual(kmp_search('ab', 'abc'), -1)

    def test_repeating_pattern(self):
        self.assertEqual(kmp_search('aaaabaaab', 'aaab'), 1)

    def test_returns_first_match_only(self):
        self.assertEqual(kmp_search('abcabc', 'abc'), 0)


class TestComputeLps(unittest.TestCase):
    def test_lps_for_simple_pattern(self):
        self.assertEqual(_compute_lps('abc'), [0, 0, 0])

    def test_lps_for_repeating_prefix(self):
        self.assertEqual(_compute_lps('aaaa'), [0, 1, 2, 3])

    def test_lps_for_abab(self):
        self.assertEqual(_compute_lps('abab'), [0, 0, 1, 2])

    def test_lps_for_aabaaa(self):
        self.assertEqual(_compute_lps('aabaaa'), [0, 1, 0, 1, 2, 2])


if __name__ == '__main__':
    unittest.main()
