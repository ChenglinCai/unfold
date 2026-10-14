# Security policy

unfold reads sources written by strangers, such as web pages, books, and slides. A source can hide instructions for a model, or point to files outside its folder. We take reports about these risks seriously.

## Report a problem

Please report a security problem privately through GitHub. Open the repository's Security tab, and choose "Report a vulnerability". Please do not open a public issue for it.

Include the steps to reproduce the problem, and a source file that shows it if you can. Leave out any private material.

## What counts

- A source that makes a model job act outside its task, or reach files that its source never named.
- A source that makes `unfold ingest` read or write outside the folders it was given.
- A plugin, hook, or server setting that runs code the user did not ask for.

## Supported versions

unfold has no release yet. We fix problems on the `main` branch.
