# DHCP and Wireless Connectivity Runbook

Document ID: NET-RB-102 | Area: Campus Network | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Symptom: Client Gets a 169.254.x.x Address
A 169.254.x.x (APIPA) address means the client asked for DHCP and got no answer. The problem is between the client and the DHCP server, not DNS.

Check in this order:
1. Scope exhaustion: open the DHCP server console and check the scope for the client's VLAN. If utilization is above 95%, no leases are available. Short-term fix: shorten the lease time (for example from 8 days to 8 hours) for that scope. Long-term fix: request a larger subnet through a normal change.
2. DHCP relay: the VLAN interface (SVI) on the distribution or core switch must have an `ip helper-address` pointing to both DHCP servers:
```
show running-config interface vlan <id> | include helper
```
   A missing helper address on a new VLAN is the most common cause after a change.
3. DHCP server service: confirm the DHCP service is running on both servers and failover is healthy.
4. Port VLAN: confirm the switch port or SSID maps to the expected VLAN.

## Symptom: Many Users in One Area Cannot Connect to Wi-Fi
1. Check the wireless controller for the access points in that area. If the APs show as down, check their switch ports for PoE (`show power inline`).
2. If APs are up but clients cannot join, check the authentication server (RADIUS) status. RADIUS timeouts cause all 802.1X SSIDs to fail at once while the guest SSID still works.
3. If clients join but get no IP address, follow the 169.254 steps above for the wireless client VLAN.

## Symptom: Wi-Fi Is Slow in a Large Room
Check AP client counts on the controller. More than 50 clients on one AP radio usually causes slow performance. Short-term: confirm band steering is moving capable clients to 5 GHz. Long-term: request a wireless survey to add APs.

## Escalation
Scope changes, new helper addresses, and RADIUS server changes are normal changes and require an approved change request (see CHG-PROC-001). Escalate RADIUS outages to the Identity team immediately as a P2 incident.
