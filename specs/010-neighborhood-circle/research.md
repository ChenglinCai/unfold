# Research: Neighborhood circle

Each entry records one design call. The maintainer was away, so Claude made each call, and each waits for the gate.

## Extend the scatter plot, or add a component

- **Decision**: the scatter plot gains an optional `query` and an optional `k`.
- **Rationale**: a neighborhood always sits on a scatter plot. One component keeps the axes, the colors, and the labels the same with or without it.
- **Alternatives considered**: a separate `neighbors` component. It would repeat the scatter plot's drawing, and the scene step would need to choose between two near twins.

## Which distance

- **Decision**: straight-line distance in the data's own units.
- **Rationale**: k-nearest-neighbors lessons start with it, and the golden requests describe a circle.
- **Alternatives considered**: a `metric` parameter for other distances. No golden lesson asked for one, so it waits.

## A circle or an oval

- **Decision**: with a query point, both axes share one scale, so the boundary draws as a circle. Spans more than three times apart keep the full-size axes, and the boundary draws as an oval.
- **Rationale**: the first still drew a wide oval, because the axes stretch to fill the region. Both of its axes measured hours, so viewers would expect a circle. A shared scale shows the true distances, and the ratio rule keeps the plot from shrinking into a strip.
- **Alternatives considered**: always an oval that follows each axis's scale. It stays correct, but it hides the idea of one distance in every direction. Always a shared scale squeezes data with very different spans.

## Ties at the k-th distance

- **Decision**: the parameter check refuses a plot whose k-th and next-nearest points sit at the same distance. Distances within one part in a billion count as equal.
- **Rationale**: the boundary would pass through a point that is not a neighbor, and viewers could not tell why. The retry feedback asks for another k or another query point.
- **Alternatives considered**: mark every tied point. The picture would then show more than k neighbors.

## How neighbors stand out

- **Decision**: each neighbor keeps its group color and gains a ring in the theme's text color. The query point is a larger dot with the same ring. A thin outline over a light shade marks the neighborhood.
- **Rationale**: the group colors carry the vote, so the mark must not replace them. A ring reads on every palette color.
- **Alternatives considered**: dimming the other points. Dimmed points lose their group colors, which the vote needs.

## The vote

- **Decision**: the query point takes the color of the group with the most neighbors. On a tie, it takes the theme's text color.
- **Rationale**: code computes the answer, so a model never states a wrong one. A tie has no answer, and a neutral color says so.
- **Alternatives considered**: a text label with the counts. It adds words that the narration should carry.

## The boundary's smallest size

- **Decision**: the drawn boundary is never smaller than about two dot widths.
- **Rationale**: a query on top of a point, with k of 1, has a distance of zero. The boundary must still show.
- **Alternatives considered**: refuse a distance of zero. A query on a training point is a fair example, so the check allows it.

## Fitting the region

- **Decision**: the axis ranges cover the points, the query point, and the whole boundary, before the usual padding.
- **Rationale**: the layout check then holds by construction, whatever the query.
- **Alternatives considered**: clip the boundary at the axes. A clipped boundary hides part of the neighborhood.
