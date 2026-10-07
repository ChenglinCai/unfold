# Eval report: M5, visuals

This report covers the scenes and renders of the 12 golden segments. Claude reviewed every contact sheet, before and after the fixes.

## What the first contact sheets showed

The first render passed every layout check, yet the contact sheets showed five failure types.

| Failure type | Example | Fix |
|---|---|---|
| Invented chart data | A bar chart of a "1990 poll" with scores that no source gives | A prompt rule, and the `chart-numbers-grounded` check, which sends such charts to review |
| Overlapping labels | Twelve yearly cash flows piled into one smear | The layout check counts overlapping labels, and timelines drop labels that would collide |
| TeX printed as text | A text card that shows `e^{i\pi}` literally | The scene check rejects TeX in a text card |
| Stage directions on screen | A card that reads "shrinks into a corner" | A prompt rule: cards hold words for the viewer, and custom cards hold the rest |
| Frames caught mid-transition | Ghosts of the last visual on the sheet | Contact sheets sample the middle of each hold |

## After the fixes

| Check | Passes | Rate |
|---|---|---|
| Layout check at render time | 12 of 12 | 100% |
| `scene-uses-components` | 11 of 12 | 92% |
| `chart-numbers-grounded` | 7 of 12 | 58% |

- 11 of 12 scenes passed their checks on the first try, and one needed a second. Before the prompt said how much text fits, several scenes needed three or four tries.
- The 5 charts that fail `chart-numbers-grounded` show computed values, such as discounted cash flows, or invented ones. A person should check each, because code cannot tell a correct computation from an invention.
- The invented poll survived as "Example 1990 poll ranking". The model kept the letter of the rule and broke its point, so the check matters more than the prompt.
