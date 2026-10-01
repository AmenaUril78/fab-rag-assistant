# Equipment Alarm Code Quick Reference

Document ID: EQ-ALM-001 | Area: All Areas | Owner: Equipment Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## How to Use This Reference
Find the alarm code shown on the tool screen, perform the first response action, and follow the linked guide. Severity A alarms stop the tool and require equipment engineer sign-off before restart. Severity B alarms allow the operator to finish the current wafer and then hold. Severity C alarms are warnings only.

## Etch Alarms
- ALM-4021 RF Reflected Power High. Severity A. First response: hold lot, put chamber in maintenance mode. Guide: ETCH-TG-014.
- ALM-4107 Endpoint Not Detected. Severity B. First response: compare OES trace with golden trace. Guide: ETCH-TG-014.
- ALM-4150 Helium Backside Leak High. Severity A. First response: check ESC helium leak rate; above 3 sccm requires ESC inspection. Guide: ETCH-TG-014.
- ALM-4300 Chamber Pressure Out of Range. Severity B. First response: check throttle valve position and pump status.

## Thin Films Alarms
- CVD-2210 Heater Over-Temperature. Severity A. First response: compare main and backup thermocouple readings. Guide: CVD-SOP-031.
- CVD-2305 Gas Flow Deviation. Severity B. First response: run MFC verification on the deviating gas line.

## CMP Alarms
- CMP-1102 Slurry Flow Low. Severity A. First response: check slurry supply pressure and line for blockage; flow below 150 mL/min stops polishing.
- CMP-1180 Pad Life Exceeded. Severity B. First response: replace pad and run the pad break-in recipe.

## Facility and Safety Alarms
- FAC-9001 Toxic Gas Detected. Severity A. First response: evacuate the area immediately and follow the gas leak response in SAFE-EMR-010. Do not attempt to locate the leak.
- FAC-9020 Exhaust Flow Low. Severity A. First response: stop processing; tool exhaust is required for safe operation.
- FAC-9105 Process Cooling Water Low Flow. Severity B. First response: check PCW valves and filter.

## Automation Alarms
- AMHS-7001 FOUP Load Port Error. Severity C. First response: check FOUP seating and RFID read; retry once, then call automation on call.
