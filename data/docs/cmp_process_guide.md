# Chemical Mechanical Planarization (CMP) Process Guide

Document ID: CMP-PG-022 | Area: CMP | Owner: CMP Process Engineering
Note: Fictional sample document created for a portfolio project ("Example Fab"). Not real fab procedure.

## Scope
CMP polishes wafers flat using a rotating pad, a slurry, and a carrier head. This guide covers copper and oxide CMP defects and consumable management.

## Consumable Life
- Polishing pad: replace after 1,200 wafers or when pad thickness falls below 1.5 mm.
- Pad conditioner disk: replace after 4,000 wafers or when removal rate drops more than 8% despite a new pad.
- Retaining ring: replace after 2,500 wafers.
Track consumable life in the tool consumables screen. Running consumables beyond life is a common cause of scratches and removal rate drift.

## Copper Dishing and Erosion
Dishing is the recess of copper lines below the surrounding dielectric, most severe in wide lines. Erosion is thinning of the dielectric in dense line areas.

Likely causes: excessive over-polish time, high down force, worn pad, or wrong slurry selectivity.

Actions:
1. Check the endpoint signal; an endpoint detected late causes excessive over-polish.
2. Reduce over-polish time in steps of 5 seconds and re-measure dishing on the test structures.
3. Confirm the barrier slurry lot and its expiration date.

## Micro-Scratches
Symptom: arc-shaped scratches found by defect inspection after CMP.

Likely causes: agglomerated slurry particles, debris on the pad, or conditioner disk diamond loss.

Actions:
1. Check slurry filter differential pressure; replace filters if pressure drop exceeds 15 psi.
2. Verify slurry was mixed and recirculated per supplier guidance. Slurry left static for more than 24 hours can agglomerate.
3. Inspect the conditioner disk under magnification for missing diamonds.
4. Run a pad break-in recipe and two defect monitor wafers before returning to production.

## Removal Rate Drift
If the oxide removal rate on the daily monitor changes more than ±6%, check slurry flow rate (target 200 mL/min), platen temperature, pad life, and conditioner disk life. Note that removal rate typically falls toward the end of pad life.

## Post-CMP Clean
Wafers must enter the post-CMP brush clean within 10 minutes of polishing. Longer queue time allows slurry to dry on the surface and causes residue defects that are very difficult to remove.
