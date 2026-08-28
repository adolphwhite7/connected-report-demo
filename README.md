# Connected Report Demo

This small Python program reads a JSON file of findings, selects the requested items, and writes one connected Markdown report with source links. It uses synthetic operations data and the Python standard library only.

## What It Does

- validates the input and rejects duplicate or incomplete findings;
- preserves the order of the selected finding IDs;
- summarizes the themes represented in the selection;
- shows how findings sharing a theme relate to one another; and
- produces a readable report with evidence, next actions, and sources.

## Try It

Requires Python 3.10 or newer.

```bash
python3 report_builder.py \
  --input examples/findings.json \
  --select F-101 F-102 F-103 \
  --output connected-report.md
```

The generated report will be written to `connected-report.md`. A committed example is available at [examples/connected-report.md](examples/connected-report.md).

## Run the Tests

```bash
python3 -m unittest discover -s tests -v
```

## Input Format

Each finding includes an ID, title, theme, summary, evidence, recommended action, and public source reference. See [examples/findings.json](examples/findings.json) for a complete sample.

## Scope

This repository is a standalone demonstration. It contains no DNA Health Insights code, customer data, private schemas, or internal operating material.

Created by [Adolph White Jr.](https://github.com/adolphwhite7).
