# Plasma Etch Chamber Troubleshooting Guide

Document ID: ETCH-TG-014 | Area: Dry Etch | Owner: Etch Equipment Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## Scope
This guide covers troubleshooting for inductively coupled plasma (ICP) etch chambers used for poly-silicon, oxide, and metal etch steps. It applies to equipment engineers and process technicians on all shifts.

## RF Reflected Power High
Symptom: Reflected RF power exceeds 10% of forward power for more than 3 seconds, or alarm ALM-4021 is raised.

Likely causes:
- Matching network capacitor drift or failing tuning motor.
- Worn or cracked quartz window causing unstable plasma impedance.
- Incorrect chamber pressure (pressure controller or throttle valve fault).
- Loose RF cable or connector at the match input.

Actions:
1. Put the chamber in maintenance mode and hold any in-process lot. Do not restart the recipe more than once.
2. Check the match tuning log. If the load and tune capacitor positions are at their travel limits, the matching network needs calibration.
3. Verify chamber pressure against the recipe set point. A deviation above 5% points to the throttle valve.
4. Inspect RF cables and connectors with RF power off and lockout applied (see SAFE-LOTO-002).
5. If reflected power remains high after calibration, inspect the quartz window for cracks or heavy deposition.

## Endpoint Detection Failure
Symptom: Optical emission spectroscopy (OES) endpoint is not triggered and the step ends on the maximum time limit, or alarm ALM-4107 is raised.

Likely causes: dirty viewport window, OES fiber misalignment, wrong endpoint wavelength in the recipe, or an incoming film thickness out of spec.

Actions:
1. Compare the OES trace with the golden trace for the same recipe.
2. Clean or replace the viewport window if signal intensity is below 60% of baseline.
3. Confirm the endpoint wavelength (for example, 405 nm for poly etch) matches the recipe.
4. Ask metrology to measure the incoming film thickness on the affected lot. Over-etch can damage the underlying layer, so wafers must be dispositioned by the process engineer before moving.

## Particle Excursion After Wet Clean
Symptom: Particle adders on monitor wafers exceed 30 adders at 0.09 µm or larger after a chamber wet clean.

Actions:
1. Run the chamber seasoning recipe (SEASON-ETCH-03) for a minimum of 25 dummy wafers.
2. Run two particle monitor wafers. If adders remain above limit, inspect the edge ring and focus ring for flaking.
3. Check that the chamber was pumped down to base pressure below 2 mTorr and passed the leak-up rate test (less than 1 mTorr per minute).

## Etch Rate Drift
Symptom: Etch rate on the daily monitor drifts more than ±4% from target.

Actions:
1. Check RF hours since last wet clean. Chambers beyond 800 RF hours commonly show etch rate drift and should be scheduled for preventive maintenance.
2. Verify gas flows using the mass flow controller (MFC) verification routine.
3. Check electrostatic chuck (ESC) helium backside leak rate. A leak above 3 sccm causes poor wafer temperature control and non-uniform etch.

## Escalation
If a problem is not resolved within 2 hours, escalate to the Etch equipment owner on call and record the event in the equipment log with the alarm code, actions taken, and lots affected.
