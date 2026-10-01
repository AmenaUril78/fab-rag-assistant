# Lessons Learned Log (Equipment and Process Incidents)

Document ID: ENG-LL-2026 | Area: All Areas | Owner: Manufacturing Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## LL-2026-011: Etch Chamber Arcing After Edge Ring Replacement
What happened: After a scheduled PM, an etch chamber showed intermittent arcing and particle excursions on 3 lots.
Root cause: The new edge ring was installed without the required torque sequence, leaving a small gap between the ring and the ESC.
Corrective action: Added a torque verification step and photo check to the PM checklist. Required a second-person sign-off for edge ring installation.
Lesson: PM checklist changes must include verification steps, not only installation steps.

## LL-2026-018: Overlay Shift After Reticle Swap
What happened: Overlay on a critical layer shifted by 3 nm on all lots after a reticle was replaced with a new revision.
Root cause: The APC system kept using correction parameters from the previous reticle because the reticle ID mapping was not updated.
Corrective action: Automated check that blocks lot dispatch when a reticle ID has no APC history. Engineers must run a send-ahead wafer for any new reticle.
Lesson: Always run a send-ahead (pilot) wafer when the reticle, recipe, or tool changes.

## LL-2026-024: CMP Scratches From Expired Slurry
What happened: Defect inspection found micro-scratches on 2 lots after copper CMP.
Root cause: A slurry tote past its shelf life was connected because the expiration date was not checked at the tote swap.
Corrective action: Added barcode scan of the slurry tote that checks the expiration date before the supply valve can open.
Lesson: Use system interlocks instead of relying on manual checks for consumable expiration.

## LL-2026-031: PECVD Thickness Excursion From Thermocouple Drift
What happened: Oxide thickness trended high over two days without an SPC rule 1 violation.
Root cause: The heater thermocouple drifted, causing the heater to run 8 °C hotter than set point.
Corrective action: Added a daily comparison between main and backup thermocouples with an alarm at 5 °C difference. The trend was visible under SPC rule 4 (eight points on one side), but the notification email was not reviewed.
Lesson: SPC trend notifications need an owner and a review deadline.
