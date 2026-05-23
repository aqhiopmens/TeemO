import unittest

from algorithms.levenshtein import levenshtein_distance


class TestLevenshteinDistance(unittest.TestCase):
    def test_both_empty(self):
        self.assertEqual(levenshtein_distance('', ''), 0)

    def test_one_empty(self):
        self.assertEqual(levenshtein_distance('', 'abc'), 3)

    def test_identical(self):
        self.assertEqual(levenshtein_distance('hello', 'hello'), 0)

    def test_single_substitution(self):
        self.assertEqual(levenshtein_distance('cat', 'bat'), 1)

    def test_single_insertion(self):
        self.assertEqual(levenshtein_distance('cat', 'cats'), 1)

    def test_single_deletion(self):
        self.assertEqual(levenshtein_distance('cats', 'cat'), 1)

    def test_classic_kitten_sitting(self):
        self.assertEqual(levenshtein_distance('kitten', 'sitting'), 3)

    def test_korean_single_substitution(self):
        self.assertEqual(levenshtein_distance('판타지', '팡타지'), 1)

    def test_symmetry_invariant(self):
        # Edit distance is symmetric: d(a, b) == d(b, a)
        self.assertEqual(
            levenshtein_distance('kitten', 'sitting'),
            levenshtein_distance('sitting', 'kitten'),
        )


if __name__ == '__main__':
    unittest.main()
