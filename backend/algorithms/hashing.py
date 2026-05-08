class BookHashTable:
    def __init__(self, size=64):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return sum(ord(c) for c in key) % self.size

    def insert(self, genre, book):
        index = self._hash(genre)
        for entry in self.table[index]:
            if entry['genre'] == genre:
                entry['books'].append(book)
                return
        self.table[index].append({'genre': genre, 'books': [book]})

    def get(self, genre):
        index = self._hash(genre)
        for entry in self.table[index]:
            if entry['genre'] == genre:
                return entry['books']
        return []

    def get_top_genres(self, n=3):
        all_genres = []
        for bucket in self.table:
            for entry in bucket:
                avg_rating = sum(b['rating'] for b in entry['books']) / len(entry['books'])
                all_genres.append({
                    'genre': entry['genre'],
                    'count': len(entry['books']),
                    'avg_rating': avg_rating,
                })
        all_genres.sort(key=lambda x: (x['avg_rating'], x['count']), reverse=True)
        return [g['genre'] for g in all_genres[:n]]
