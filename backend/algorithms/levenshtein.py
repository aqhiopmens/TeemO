"""Levenshtein (edit) distance via dynamic programming.

Computes the minimum number of single-character edits — insertions,
deletions, or substitutions — required to transform one string into
another. Used by the ``/api/search`` endpoint as a fuzzy fallback when
the exact (KMP) title search returns no matches.

Time complexity:  O(m * n) — fills an (m+1) x (n+1) DP table
Space complexity: O(m * n) — the full 2D table is retained
where m = len(s1), n = len(s2).

Pure module: no Flask / framework imports.
"""


def levenshtein_distance(s1: str, s2: str) -> int:
    """Return the Levenshtein edit distance between ``s1`` and ``s2``.

    Standard bottom-up DP over a 2D table where ``dp[i][j]`` is the edit
    distance between the first ``i`` characters of ``s1`` and the first
    ``j`` characters of ``s2``.

    Works on any Unicode strings (e.g. Korean), since iteration is over
    code points.

    Time:  O(m * n)
    Space: O(m * n)
    """
    m, n = len(s1), len(s2)

    # dp[i][j] = edit distance between s1[:i] and s2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: cost of transforming to/from the empty string
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,         # deletion
                dp[i][j - 1] + 1,         # insertion
                dp[i - 1][j - 1] + cost,  # substitution (or match when cost=0)
            )

    return dp[m][n]
