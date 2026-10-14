# Data model: Neighborhood circle

The scatter plot keeps every parameter it had. It gains two optional ones.

| Parameter | Type | Rule |
|---|---|---|
| `query` | a pair of numbers, x then y | Needs `k`. |
| `k` | a whole number | Needs `query`. It runs from 1 to the number of points. |

## Checks

A scene fails its check, with a message for the retry, when:

- it gives `query` without `k`, or `k` without `query`.
- `k` is below 1, or above the number of points.
- the k-th and next-nearest points sit at the same distance from the query.

## What code computes

- **Neighbors**: the k points nearest the query, by straight-line distance.
- **Reach**: the distance to the k-th nearest point.
- **Vote**: the group with the most neighbors, or none on a tie. A plot without groups puts every point in group 0.

## Example

```yaml
visual:
  component: scatter-plot
  points: [[1, 1], [2, 1.5], [1.5, 3], [4, 4], [5, 3.5], [4.5, 5]]
  groups: [0, 0, 0, 1, 1, 1]
  x_label: hours studied
  y_label: hours slept
  query: [3, 3]
  k: 3
```

Here the three nearest points are (4, 4), (1.5, 3), and (2, 1.5). Two of them are group 0, so the query point takes group 0's color.
