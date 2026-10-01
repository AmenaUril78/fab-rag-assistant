# Change Management Procedure

Document ID: CHG-PROC-001 | Area: All IT | Owner: IT Service Management
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Change Types
- Standard change: pre-approved, low risk, repeatable (for example, re-enabling an access port or updating a single DNS record). No CAB review needed; record it in the ticket.
- Normal change: any change that is not pre-approved. Requires a change request and approval by the Change Advisory Board (CAB), which meets every Tuesday. Submit by Friday 17:00 for the next CAB.
- Emergency change: needed to restore service during an active P1 or P2 incident. Requires verbal approval from the on-call manager; the change request must be completed within 1 business day after the fix.

## Required Sections in a Change Request
1. Description and business reason.
2. Affected devices and services, and expected user impact.
3. Implementation plan: step-by-step commands or actions.
4. Pre-checks: what to verify and capture before starting (for example, `show interfaces status`, routing table, current config backup).
5. Post-checks: how to confirm success.
6. Rollback plan: exact steps to undo the change, and the rollback trigger.
7. Maintenance window and communication plan.

## Maintenance Windows
Changes with user impact must run in the maintenance window: Sunday 02:00 to 06:00. Changes to core routers, firewalls, or DHCP/DNS servers always require a maintenance window.

## Rollback Criteria
Roll back if any post-check fails and cannot be fixed within 30 minutes, or if unexpected user impact is reported. Do not try new untested fixes inside the window; roll back and reschedule.

## After the Change
Close the change with the result (successful, rolled back, or partially completed) and attach post-check output. A failed change requires a short review at the next CAB.
