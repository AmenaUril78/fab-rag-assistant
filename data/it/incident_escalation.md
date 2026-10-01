# Incident Severity and Escalation Guide

Document ID: INC-PROC-002 | Area: All IT | Owner: IT Service Management
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Severity Levels
- P1 (Critical): a core service is down for a large population or a whole site (for example, campus internet outage, core router failure, authentication down). Response within 15 minutes, 24x7.
- P2 (High): a service is degraded for many users or down for one building or department (for example, one building switch stack down, Wi-Fi authentication failing). Response within 30 minutes, 24x7.
- P3 (Medium): a single user or small group is affected and a workaround exists. Response within 4 business hours.
- P4 (Low): a request or minor issue. Response within 2 business days.

## P1 and P2 Process
1. The on-call engineer acknowledges the page and opens a bridge call.
2. Assign an incident commander (usually the on-call lead) and a communications owner.
3. Post a status update every 30 minutes for P1 and every 60 minutes for P2, even if nothing changed.
4. Emergency changes are allowed with verbal approval from the on-call manager (see CHG-PROC-001).
5. After service is restored, schedule a postmortem within 5 business days.

## Escalation Path
Tier 1 (Service Desk) to Tier 2 (Network Operations) to Tier 3 (Network Engineering) to the vendor. Escalate to the next tier if no progress is made in 30 minutes for a P1 or 2 hours for a P2.

## On-Call Expectations
The on-call engineer must respond to a page within 15 minutes and be able to connect to VPN within 30 minutes. If you cannot respond, call the backup on-call engineer.
