# PECVD Tool Preventive Maintenance and Film Issues

Document ID: CVD-SOP-031 | Area: Thin Films | Owner: Thin Films Equipment Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## Scope
Plasma-enhanced chemical vapor deposition (PECVD) tools deposit silicon oxide and silicon nitride films. This SOP covers preventive maintenance (PM) intervals and common film quality problems.

## Preventive Maintenance Intervals
- Remote plasma clean (NF3): automatically every 1,500 nm of cumulative deposition.
- Showerhead inspection: every 2,000 wafers.
- Full chamber PM (showerhead replacement, heater inspection, O-ring replacement): every 12,000 wafers or 90 days, whichever comes first.
- Throttle valve and pressure gauge calibration: every 6 months.

## Post-PM Qualification
After a full chamber PM, the tool must pass all of the following before release to production:
1. Leak-up rate below 2 mTorr per minute.
2. Deposition rate within ±3% of target on two monitor wafers.
3. Thickness non-uniformity below 2.0% (1-sigma, 49-point map).
4. Particle adders below 20 at 0.09 µm or larger.
5. Film stress within the specification for the film type (oxide: -150 to -250 MPa compressive).
Record all results in the qualification checklist and get sign-off from the shift equipment lead.

## Thickness Non-Uniformity Above Limit
Symptom: 49-point thickness map shows non-uniformity above 2.0%, often as a center-thick or edge-thick pattern.

Likely causes and actions:
- Center-thick pattern: showerhead holes partially clogged in the center. Inspect and clean or replace the showerhead.
- Edge-thick pattern: heater temperature profile drift. Run the heater zone calibration and confirm the edge zone is within ±2 °C of set point.
- Random pattern: spacing between showerhead and heater is incorrect. Verify the spacing (typically 400 mils) with the gap gauge.

## Film Stress Out of Specification
Symptom: Wafer bow measurement shows film stress outside specification.

Actions: verify RF power and frequency mix (high-frequency vs. low-frequency power ratio controls stress), confirm SiH4 and N2O or NH3 flows with MFC verification, and check heater temperature. Hold the lot and notify the thin films process engineer.

## Alarm CVD-2210: Heater Over-Temperature
The heater interlock trips when the pedestal heater exceeds set point by 25 °C. Do not reset the interlock repeatedly. Check the thermocouple reading against the backup thermocouple. A difference greater than 10 °C indicates a failing thermocouple that must be replaced before the tool returns to service.
