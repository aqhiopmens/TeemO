import unittest

from algorithms.greedy import greedy_preference_score


def book(genre, rating):
    return {'genre': genre, 'rating': rating}


class TestGreedyPreferenceScore(unittest.TestCase):
    def test_empty_returns_empty(self):
        self.assertEqual(greedy_preference_score([]), {})

    def test_single_book_normalizes_to_one(self):
        scores = greedy_preference_score([book('Fiction', 5)])
        self.assertEqual(list(scores.keys()), ['Fiction'])
        self.assertAlmostEqual(scores['Fiction'], 1.0, places=3)

    def test_scores_sum_to_approximately_one(self):
        books = [book('A', 5), book('B', 4), book('C', 3), book('A', 2)]
        scores = greedy_preference_score(books)
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=2)

    def test_higher_rated_genre_scores_higher(self):
        books = [book('Top', 5), book('Mid', 3), book('Low', 1)]
        scores = greedy_preference_score(books)
        self.assertGreater(scores['Top'], scores['Mid'])
        self.assertGreater(scores['Mid'], scores['Low'])

    def test_missing_genre_falls_back_to_unknown(self):
        scores = greedy_preference_score([{'rating': 4}])
        self.assertIn('Unknown', scores)

    def test_earlier_position_gets_rank_bonus(self):
        # Two books with identical rating: the one appearing first in the
        # sorted list should accumulate more weight from the rank bonus.
        scores = greedy_preference_score([book('First', 4), book('Second', 4)])
        self.assertGreater(scores['First'], scores['Second'])


if __name__ == '__main__':
    unittest.main()
