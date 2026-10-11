# Security policy

## Report a problem in private

Report a security problem through GitHub's private reporting. Open this repository's Security tab, and choose "Report a vulnerability". Only the maintainer sees the report.

Please do not open a public issue for a security problem.

## What matters most

unfold reads files and web pages that strangers wrote, and it runs model jobs on the user's own account. These reports matter most:

- A source file that makes unfold read files outside its folder, or reach the network.
- A source that makes a model job run with tools or permissions that it should not have.
- Output from a private source that reaches a public page, such as the gallery.
- Anything that leaks a user's files, keys, or account.

## What happens next

The maintainer reads each report and replies in the same private thread. A confirmed problem gets a fix and a test, and the fix's pull request credits the reporter, unless the reporter asks otherwise.

## Versions

unfold has no release yet, so fixes land on the main branch.
