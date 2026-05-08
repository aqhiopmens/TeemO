def merge_sort(books, key='rating', reverse=True):
    if len(books) <= 1:
        return books

    mid = len(books) // 2
    left = merge_sort(books[:mid], key, reverse)
    right = merge_sort(books[mid:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_val = left[i][key]
        right_val = right[j][key]
        if (left_val >= right_val) if reverse else (left_val <= right_val):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
