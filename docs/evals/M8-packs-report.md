# Eval report: M8, domain packs

Four new components replaced most of the custom visuals in the golden set. This report compares the 14 golden scenes before the change with three rebuild rounds after it. The scenes hold 96 beats from six sources in five families. Examples come only from sources that allow public outputs.

## What changed

The components are `complex-plane` for math, `histogram` for statistics, `present-value` for economics and finance, and `flow-diagram` for any subject. The component version rose from 3 to 4, so every scene and render rebuilt. Earlier steps reused their saved results.

| Round | What the scene step had |
|---|---|
| 1 | The four components, and prompt text for each |
| 2 | A rule from reading round 1: show the picture that a described motion ends on, if a component can draw it |
| 3 | A rule and a check from reading the round 2 contact sheets: labels outside an equation are plain text, with no TeX |

## Results

| Measure | Before | Round 1 | Round 2 | Round 3 |
|---|---|---|---|---|
| Custom beats | 27 of 96, or 28% | 18, or 19% | 12, or 12.5% | 13, or 13.5% |
| `scene-uses-components` | 13 of 14 | 13 of 14 | 14 of 14 | 14 of 14 |
| `chart-numbers-grounded` | 7 of 14 | 8 of 14 | 8 of 14 | 7 of 14 |
| Layout failures at render | 0 | not rendered | 0 | 0 |

- The other seven checks never read scenes, and none of them changed.
- Round 3 misses the spec's goal of at most 10 percent, so SC-001 fails. The next section says what the rest would need.
- No scene check passes less often than before, so SC-004 holds. `chart-numbers-grounded` moves between 7 and 8 from round to round, because the model's choices vary.
- The three rounds made 70 model calls: 18 canaries, 42 first tries, and 10 retries. In round 3, every retry came from the layout check, for text that was too small or labels that overlapped.

| Series | Family | Custom before | Custom after |
|---|---|---|---|
| Central limit theorem | topic | 6 of 13 | 5 of 13 |
| CIS 5200, k-NN | textbook | 2 of 15 | 3 of 15 |
| Euler's identity | web | 5 of 11 | 0 of 11 |
| MIT 18.05 | slides | 3 of 15 | 1 of 15 |
| Net present value | web | 6 of 30 | 2 of 30 |
| Velocity of money | recording | 5 of 12 | 2 of 12 |

The flow diagram proved the most flexible, with 13 uses across five series. Euler's identity uses 6 complex planes. Histograms and present-value charts appear less often, because the model often keeps a bar chart for counts.

## What the last 13 custom beats need

| Need | Beats | Example from a public source |
|---|---|---|
| Motion that carries the idea | 6 | A die tumbles and lands, in the central limit theorem |
| A picture that no component draws | 5 | A histogram tips and settles on a pencil, at its balance point |
| A neighborhood circle on a scatter plot | 2 | Both come from the private CIS 5200 source |

Round 1 asked for the neighborhood circle three times, which meets the plan's rule for a new component. The machine-learning pack could start there.

## What the contact sheets showed

- **TeX in labels.** In round 2, three complex-plane beats printed labels such as `e^{2πi} = 1`, braces and all. Round 3's check and rule fixed all three, so the labels now read `e^(2πi) = 1` and `z·e^(iθ)`.
- **Flat bars beside a large outflow.** In the net-present-value verdict, an outflow of 100,000 dwarfs twelve payments of 10,000. The total stays right, at -31,863, but the shrinking is hard to see.
- **Off-center link labels.** A label on a straight link sat about 0.03 units from one box, because an arrow's shaft stops where its tip starts. Each label now centers between the arrow's ends and clears both boxes by 0.2.
- **Split words.** A narrow box broke a long word across two lines. Box labels now keep words whole, and a box grows to fit its widest word.
- **Correct numbers.** Each present value matches the formula. The verdict's total also matches the decision card on the next beat.
- **Inventive uses.** One flow diagram chains i, π, e, 1, and 0 with the signs that join them in Euler's identity.

## Decisions for the maintainer

- Keep both prompt rules. Against the starting point, every scene check improved or held, as principle IV requires.
- SC-001 needs a call. Accept 13.5 percent, or ask for the next components: a neighborhood circle for scatter plots, and motion inside a component.
