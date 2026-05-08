def greedy_preference_score(sorted_books):
    """
    Assigns genre preference weights greedily: higher-rated books and
    books ranked earlier in the sorted list contribute more weight.
    Returns a normalized score dict {genre: score}.
    """
    genre_scores = {}
    total = len(sorted_books)

    for i, book in enumerate(sorted_books):
        genre = book.get('genre', 'Unknown')
        rating = book.get('rating', 0)
        # Rank bonus: books earlier in the sorted list (higher rating) weigh more
        weight = rating * (1 + (total - i) / total)
        genre_scores[genre] = genre_scores.get(genre, 0) + weight

    total_weight = sum(genre_scores.values()) or 1
    return {genre: round(score / total_weight, 3) for genre, score in genre_scores.items()}
