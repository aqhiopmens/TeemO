import unittest

from algorithms.merge_sort import merge_sort


def book(title, rating):
    return {'title': title, 'rating': rating}


class TestMergeSort(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(merge_sort([]), [])

    def test_single_element(self):
        self.assertEqual(merge_sort([book('A', 3)]), [book('A', 3)])

    def test_sorts_descending_by_rating_by_default(self):
        books = [book('A', 2), book('B', 5), book('C', 3)]
        result = merge_sort(books)
        self.assertEqual([b['rating'] for b in result], [5, 3, 2])

    def test_sorts_ascending_when_reverse_false(self):
        books = [book('A', 2), book('B', 5), book('C', 3)]
        result = merge_sort(books, reverse=False)
        self.assertEqual([b['rating'] for b in result], [2, 3, 5])

    def test_stable_for_equal_keys(self):
        books = [book('first', 4), book('second', 4), book('third', 4)]
        result = merge_sort(books)
        self.assertEqual([b['title'] for b in result], ['first', 'second', 'third'])

    def test_does_not_mutate_input(self):
        books = [book('A', 2), book('B', 5)]
        original = list(books)
        merge_sort(books)
        self.assertEqual(books, original)

    def test_custom_key(self):
        items = [{'name': 'a', 'score': 1}, {'name': 'b', 'score': 9}]
        result = merge_sort(items, key='score')
        self.assertEqual([i['score'] for i in result], [9, 1])


if __name__ == '__main__':
    unittest.main()
