# Lithography Overlay and CD Control Guide

Document ID: LITHO-PG-007 | Area: Photolithography | Owner: Litho Process Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## Scope
This guide explains how to respond when overlay or critical dimension (CD) measurements fall outside control limits on scanner and track systems.

## Key Terms
- Overlay: the alignment error between the current layer and a previous layer, measured in nanometers in X and Y.
- CD (critical dimension): the measured width of a printed feature, usually measured by CD-SEM after develop (ADI) and after etch (AEI).
- Focus and dose: the two main scanner settings that control CD. Dose controls exposure energy; focus controls the image plane position.
- Rework: stripping the photoresist and re-exposing the wafer. Rework is only possible before etch.

## Overlay Out of Specification
Symptom: overlay mean plus 3-sigma exceeds the layer specification (for example, 4.0 nm for a critical layer) on the after-develop inspection.

Actions:
1. Check whether the excursion is lot-wide or limited to specific wafers. Single-wafer problems often come from wafer chuck contamination or backside particles.
2. Review the scanner alignment marks quality report. Damaged or low-contrast alignment marks are a common cause after a CMP step.
3. Confirm the correct overlay correction model was applied by the automated process control (APC) system. A missing feedback update after a reticle change causes systematic shift.
4. If the root cause is confirmed and corrected, send the lot to rework. Rework is limited to 2 times per layer because each rework degrades the underlying surface.

## CD Drift
Symptom: ADI CD trends more than 1.5 nm away from target across three or more consecutive lots.

Likely causes:
- Dose drift from the scanner light source.
- Track hot plate temperature drift in the post-exposure bake (PEB). A 1 °C change in PEB temperature can shift CD by several nanometers for chemically amplified resists.
- New photoresist lot with different sensitivity.
- Reticle haze or contamination.

Actions: run the focus-exposure matrix (FEM) monitor wafer, check PEB plate temperature logs, confirm the resist lot number, and request a reticle inspection if haze is suspected.

## Reticle Handling
Reticles must be inspected after every 50,000 exposures or whenever a repeating defect is found at the same location on every die. Never open a reticle pod outside the reticle stocker area.
