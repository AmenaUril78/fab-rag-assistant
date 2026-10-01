# IT Operations Postmortems

Document ID: OPS-PM-2026 | Area: All IT | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's incidents.

## PM-2026-04: Building Outage After VLAN Pruning Change
What happened: After a trunk cleanup change, users in one building lost connectivity for 40 minutes.
Root cause: The implementation plan removed VLAN 210 from the uplink trunk, but VLAN 210 was still used by the building's printers and badge readers. The pre-check did not list VLANs in use on access ports.
Corrective action: Pre-checks for trunk changes must include `show vlan brief` and `show interfaces trunk` on both ends. Rollback was added as a ready-to-paste command set.
Lesson: Before removing anything from a trunk, prove it is unused.

## PM-2026-07: Config Backups Silently Failing for Two Weeks
What happened: A switch failed and the latest available configuration backup was 15 days old.
Root cause: The backup service account password was rotated, and the backup job failed with authentication errors on 120 devices. The daily report email went to a mailbox nobody was monitoring.
Corrective action: Backup failures now create a ticket automatically instead of only sending email. Credential rotation now includes a checklist item to update the automation vault.
Lesson: Alerts that nobody owns are the same as no alerts.

## PM-2026-09: DHCP Exhaustion During Orientation Week
What happened: Students in the student union received 169.254 addresses on Wi-Fi during orientation events.
Root cause: The wireless client scope was a /23 (about 500 addresses) with an 8-day lease. Thousands of visiting devices used up all leases.
Corrective action: The scope was moved to a /21 and the lease time for high-traffic wireless VLANs was set to 4 hours.
Lesson: Review DHCP scope utilization before large events.

## PM-2026-11: Expired Certificate Broke Wi-Fi Authentication
What happened: All 802.1X Wi-Fi users failed to connect at 08:00 on a Monday, a P1 incident lasting 70 minutes. The guest network still worked.
Root cause: The RADIUS server certificate expired. Renewal reminders were sent to a former employee.
Corrective action: Certificates are now tracked in a shared calendar with 60-, 30-, and 7-day reminders to a team mailbox.
Lesson: If every 802.1X SSID fails at once but guest works, check RADIUS and its certificate first.
