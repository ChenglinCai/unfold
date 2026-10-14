"""Nearest points, ties, and the vote. No manim, so tests and checks run fast.

The scatter plot draws only what these functions compute, so a model never
names a neighbor or a winning group.
"""

import math
from collections import Counter
from collections.abc import Sequence

Point = Sequence[float]


def _distances(points: Sequence[Point], query: Point) -> list[float]:
    return [math.dist(point, query) for point in points]


def nearest(points: Sequence[Point], query: Point, k: int) -> list[int]:
    """The indexes of the k points nearest the query, nearest first."""
    distances = _distances(points, query)
    return sorted(range(len(points)), key=lambda i: (distances[i], i))[:k]


def reach(points: Sequence[Point], query: Point, k: int) -> float:
    """The distance from the query to its k-th nearest point."""
    return sorted(_distances(points, query))[k - 1]


def tied(points: Sequence[Point], query: Point, k: int) -> bool:
    """Whether a point outside the k nearest sits at the k-th distance too."""
    distances = sorted(_distances(points, query))
    if k >= len(distances):
        return False
    return math.isclose(distances[k - 1], distances[k], rel_tol=1e-9, abs_tol=1e-12)


def vote(groups: Sequence[int], neighbors: Sequence[int]) -> int | None:
    """The group with the most neighbors, or None on a tie. No groups means group 0."""
    counts = Counter(groups[i] if groups else 0 for i in neighbors).most_common()
    if len(counts) > 1 and counts[0][1] == counts[1][1]:
        return None
    return counts[0][0]
