# Connected Operations Review

## Executive Summary

This report connects 3 selected findings across 2 themes: Intake quality and Case routing.

Together, the findings support this practical sequence:

1. Validate the required intake fields before a request enters the assignment queue
2. Replace overlapping escalation labels with one short controlled list and an explicit fallback category
3. Require one source label and link for every submitted finding before review begins

## How the Findings Connect

- **Intake quality:** F-101 and F-103 identify related parts of the same operating issue; reviewing them together prevents one fix from leaving the other cause in place.
- **Case routing:** F-102 adds a distinct constraint that should be addressed alongside the other selected findings.

## Selected Findings

### F-101 — Incomplete intake records delay assignment

**Theme:** Intake quality

Requests missing an owner, due date, or source reference require manual follow-up before work can begin.

**Evidence**

- 12 of 40 sampled requests were missing at least one required intake field.
- Eight of those requests waited more than one business day for clarification.

**Recommended action:** Validate the required intake fields before a request enters the assignment queue.

**Source:** [Synthetic intake audit](https://example.com/#intake-audit)

### F-102 — Escalations use inconsistent categories

**Theme:** Case routing

Similar escalation reasons are recorded under several labels, which makes routing and trend review less reliable.

**Evidence**

- Five labels were used for the same access-related escalation pattern.
- Two cases were routed to the wrong queue before being reassigned.

**Recommended action:** Replace overlapping escalation labels with one short controlled list and an explicit fallback category.

**Source:** [Synthetic routing review](https://example.com/#routing-review)

### F-103 — Missing source notes increase rework

**Theme:** Intake quality

Reviewers repeat discovery work when a request states a conclusion without linking the note, record, or observation that supports it.

**Evidence**

- Nine sampled requests required a second source lookup.
- The repeated lookup added an estimated 95 minutes across the sample.

**Recommended action:** Require one source label and link for every submitted finding before review begins.

**Source:** [Synthetic rework sample](https://example.com/#rework-sample)

## Selection Record

Included finding IDs: F-101, F-102, F-103
