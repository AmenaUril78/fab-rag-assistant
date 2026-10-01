# SPC Out-of-Control Action Plan (OCAP)

Document ID: QA-OCAP-003 | Area: Quality / All Process Areas | Owner: Quality Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## Purpose
Statistical process control (SPC) charts monitor key process parameters such as film thickness, CD, overlay, and particle counts. This document defines what to do when a chart shows an out-of-control (OOC) or out-of-spec (OOS) point.

## Definitions
- Control limits: statistical limits calculated from process data, usually ±3 sigma from the mean.
- Specification limits: engineering limits that define whether the product is acceptable.
- OOC: a point or pattern that violates SPC rules but may still be inside specification.
- OOS: a measurement outside specification limits. OOS always requires a lot hold.

## SPC Rules Used (Western Electric)
1. One point beyond 3 sigma.
2. Two of three consecutive points beyond 2 sigma on the same side.
3. Four of five consecutive points beyond 1 sigma on the same side.
4. Eight consecutive points on the same side of the center line.

## Response Steps
1. The SPC system automatically places the lot on hold and inhibits the tool for that recipe when rule 1 is violated or any point is OOS.
2. The operator re-measures the wafer to rule out a metrology error. If the re-measurement is in control, document the metrology error and release.
3. If the OOC is confirmed, the equipment engineer checks the tool for the cause using the area troubleshooting guide.
4. The process engineer dispositions the held lot: release, rework, scrap, or engineering hold for more data.
5. The tool is released only after a passing monitor wafer.
6. Record the root cause and corrective action in the OCAP log within 24 hours.

## Rules 2 to 4 (Trends)
Trend violations do not automatically hold the lot. They trigger an email notification to the area engineer, who must review the chart within one shift and document the assessment.
