import unittest

from algorithms.hashing import BookHashTable


def book(title, genre, rating):
    return {'title': title, 'genre': genre, 'rating': rating}


class TestBookHashTable(unittest.TestCase):
    def test_get_returns_empty_for_unknown_genre(self):
        table = BookHashTable()
        self.assertEqual(table.get('Sci-Fi'), [])

    def test_insert_and_get_single_book(self):
        table = BookHashTable()
        b = book('Dune', 'Sci-Fi', 5)
        table.insert('Sci-Fi', b)
        self.assertEqual(table.get('Sci-Fi'), [b])

    def test_insert_groups_books_by_genre(self):
        table = BookHashTable()
        a = book('Dune', 'Sci-Fi', 5)
        b = book('Foundation', 'Sci-Fi', 4)
        table.insert('Sci-Fi', a)
        table.insert('Sci-Fi', b)
        self.assertEqual(table.get('Sci-Fi'), [a, b])

    def test_separate_chaining_keeps_genres_isolated(self):
        # Two genres with identical hash values must not collide into one bucket entry.
        table = BookHashTable(size=4)
        x = book('X', 'ab', 3)
        y = book('Y', 'ba', 4)
        table.insert('ab', x)
        table.insert('ba', y)
        self.assertEqual(table.get('ab'), [x])
        self.assertEqual(table.get('ba'), [y])

    def test_get_top_genres_orders_by_avg_rating_then_count(self):
        table = BookHashTable()
        table.insert('Fantasy', book('F1', 'Fantasy', 5))
        table.insert('Fantasy', book('F2', 'Fantasy', 5))
        table.insert('Mystery', book('M1', 'Mystery', 3))
        table.insert('History', book('H1', 'History', 4))
        top = table.get_top_genres(2)
        self.assertEqual(top, ['Fantasy', 'History'])

    def test_get_top_genres_respects_n(self):
        table = BookHashTable()
        for i, g in enumerate(['A', 'B', 'C', 'D']):
            table.insert(g, book(f'b{i}', g, 5))
        self.assertEqual(len(table.get_top_genres(2)), 2)
        self.assertEqual(len(table.get_top_genres(10)), 4)

    def test_get_top_genres_empty_table(self):
        self.assertEqual(BookHashTable().get_top_genres(3), [])


if __name__ == '__main__':
    unittest.main()
