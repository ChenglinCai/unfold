# Data model: Domain packs

Each new component is one more choice for a scene entry's `visual` in `scene/v0`. The `component` field names the choice, and the other fields are its parameters. A scene may leave out any field that has a default. Every model forbids unknown fields, like the five existing components.

## `complex-plane`

| Field | Type | Rule |
|---|---|---|
| `points` | list of points | 1 to 6 |
| `unit_circle` | true or false | default true |
| `rays` | true or false | default true. Draws a line from zero to each point |
| `turn` | turn, or nothing | an arc that marks an angle |

A point has these fields:

| Field | Type | Rule |
|---|---|---|
| `label` | text | may be empty |
| `radius` | number | from 0 to 100 |
| `angle` | number | degrees, counterclockwise from the positive real axis |
| `guides` | true or false | default false. Draws dashed lines to both axes |
| `real_label` | text | names the guide's foot on the real axis, such as "cos x" |
| `imag_label` | text | names the guide's foot on the imaginary axis, such as "sin x" |

A turn has a `start` and an `end` in degrees, and a `label`. The end may pass 360, which draws a full loop.

## `histogram`

| Field | Type | Rule |
|---|---|---|
| `edges` | list of numbers | 2 to 41, each greater than the one before |
| `counts` | list of numbers | one fewer than the edges, none below zero |
| `labels` | list of text | empty, or one per bin |
| `mean` | number, or nothing | draws a dashed mean line |
| `spread` | number, or nothing | above zero. The standard deviation |
| `curve` | true or false | default false. Needs both `mean` and `spread` |
| `highlight` | bin index, or nothing | colors one bar |
| `title` | text | may be empty |
| `x_label` | text | may be empty |

## `present-value`

| Field | Type | Rule |
|---|---|---|
| `rate` | number | percent per period, from 0 to 100 |
| `flows` | list of flows | 1 to 24 |
| `total` | true or false | default true. Shows the sum of the present values |
| `prefix` | text | at most 3 characters, such as "$" |
| `title` | text | may be empty |

A flow has `at`, its time in periods from 0 to 100, and a nonzero `amount`. A negative amount is money paid out.

Derived values, computed by code:

- A flow's present value is its amount divided by one plus the rate over 100, raised to the power of its time.
- The total is the sum of every flow's present value.

## `flow-diagram`

| Field | Type | Rule |
|---|---|---|
| `boxes` | list of boxes | 2 to 6, with unique ids |
| `links` | list of links | 0 to 10 |
| `direction` | `right` or `down` | default `right` |
| `highlight` | box id, or nothing | must name a box |

A box has an `id`, in lower-case letters, digits, and dashes, and a `label`. A link has `from` and `to`, which name two different boxes, and an optional `label`.

## Validation messages

Each rule above fails with a message that names the field, so a retry can fix it:

- "a histogram needs one count for each bin"
- "a histogram's edges must increase"
- "a bell curve needs a mean and a spread"
- "a histogram needs one label for each bin, or none"
- "link from X names no box"
- "a link must join two different boxes"
- "box ids must be unique"
