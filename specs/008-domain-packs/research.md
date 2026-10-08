# Research: Domain packs

Each entry records a decision, why we chose it, and what else we weighed. The maintainer is away, so Claude made these calls under principle VIII. Each one waits for review at the gate.

## D1. Property tests with Hypothesis, as a dev-only dependency

- **Decision**: add Hypothesis to the dev group. A property test draws each new component with random valid parameters, then checks that the drawing fits its region and shows no overlapping labels.
- **Rationale**: hand-picked examples miss the inputs that break a layout, such as twelve close flows or a long box label. The plan's platform row names tests with random inputs. Hypothesis uses the MPL-2.0 license, and users never install it.
- **Settings**: `deadline=None`, because one drawing can take longer than the default 200 milliseconds. About 25 examples per component keep the run short. On CI, Hypothesis derandomizes by default, so CI runs repeat exactly. Its example database lives in `.hypothesis/`, which git ignores.
- **Alternatives**: parametrized cases only, which cover what we already imagined. Polyfactory, which builds Pydantic models at random but cannot aim at layout edge cases.

## D2. The complex plane counts angles in degrees, with an explicit turn

- **Decision**: each point has a radius and an angle in degrees. An optional `turn` draws an arc with an arrow tip from a start angle to an end angle, with a label.
- **Rationale**: storyboards speak of "60 degrees" and "a full turn". One explicit arc covers both "rotate by theta" and "one full loop".
- **Alternatives**: radians, which need decimal values such as 1.047. An arc tied to the first point, which cannot show a rotation between two points.

## D3. Code computes every present value

- **Decision**: one pure function computes a flow's present value as its amount divided by one plus the rate, raised to its time. One function formats every shown number. The drawing and the tests both call them.
- **Rationale**: SC-003 compares each shown number with the formula. One source of truth keeps the label and the test in step.
- **Format**: values of 1,000 or more show whole units with separators. Smaller values show at most two decimals, without trailing zeros.

## D4. A present-value bar has an outline and a fill

- **Decision**: at each time, an outline bar shows the amount when paid, and a filled bar inside it shows what that amount is worth today. Labels show the worth-today values, and labels that would touch a neighbor drop out. A legend names both bars, and a line gives the total.
- **Rationale**: the shrink from outline to fill shows discounting at a glance, with no motion.
- **Alternatives**: two rows, one for future amounts and one for today, which need twice the height. Moving boxes, which need motion inside a component, and the spec leaves that out.

## D5. The histogram draws touching bars, a mean line, a spread, and a curve

- **Decision**: bins come from edges, so bars touch. A dashed line marks the mean. A double arrow spans one spread on each side of the mean. The bell curve is the normal curve with that mean and spread, scaled to the histogram's area. Optional labels name each bin, such as die faces.
- **Rationale**: these parts cover all five central limit theorem beats. Bin labels keep dice readable, since edges such as 0.5 and 1.5 are not.

## D6. The flow diagram lays boxes in one row or one column

- **Decision**: boxes sit in a row from left to right, or in a column from top to bottom. An arrow between neighbors is straight. Any other arrow curves, forward ones on one side and backward ones on the other. A diagram may have boxes and no arrows.
- **Rationale**: the golden cases are short pipelines, one cycle of three, and three boxes with question marks. Opposite arrows between two boxes curve apart, so both stay visible.
- **Alternatives**: a graph-layout library such as Graphviz, which would add a runtime dependency. A circle layout, which suits cycles but reads less like the narration's order.

## D7. The grounded-numbers check learns the new components

- **Decision**: `chart-numbers-grounded` also checks present-value amounts and rates, and histogram means and spreads. It skips histogram counts, which describe a shape, and present values, which code computes.
- **Rationale**: invented numbers were the worst M5 failure, so model-supplied numbers stay checked. Old scenes hold none of the new components, so the before numbers do not change.
- **Risk**: a model could invent counts. The eval report lists every histogram for a person to read.

## D8. `unfold eval` reports the custom share

- **Decision**: `unfold eval` adds a line with custom beats out of all scene beats, in text and in JSON.
- **Rationale**: the before and after numbers then come from one command, not from a one-off script. The review page can show it later.

## D9. The storyboard prompt waits

- **Decision**: this feature leaves the storyboard prompt alone. It still names `axes` and `number-line`, which no component draws, and a later feature fixes that.
- **Rationale**: a storyboard change would rebuild every storyboard, so the comparison would mix two changes. The spec also expects only the scene step to call a model.

## D10. The component version rises from 3 to 4

- **Decision**: raise `params.VERSION` once, with the first new component.
- **Effect**: every scene key and render key changes. The rebuild makes 12 scene calls, then 12 renders and 6 episode stitches. Earlier steps keep their saved results, because their keys leave the version out.

## D11. New components use plain text, not LaTeX

- **Decision**: labels such as θ and π use plain text, never TeX.
- **Rationale**: LaTeX is optional since M7, and the quickstart machine lacks it. Plain text also draws faster.
