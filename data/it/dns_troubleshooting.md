# DNS Troubleshooting Guide

Document ID: NET-RB-103 | Area: Core Services | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Quick Test: Is It DNS?
If a site works by IP address but not by name, the problem is name resolution. Test from the affected client:
```
nslookup <hostname>
nslookup <hostname> <other-dns-server-ip>
```
On macOS or Linux you can use `dig <hostname>` for more detail.

## Reading the Result
- NXDOMAIN: the name does not exist in DNS. Check the spelling, then check whether the record was deleted or never created. Ask the system owner.
- SERVFAIL: the DNS server could not complete the lookup. This often points to a broken forwarder, a DNSSEC validation failure, or an unreachable authoritative server.
- Timeout: the client cannot reach the DNS server. Check the client's DNS server settings and firewall rules for UDP and TCP port 53.
- Wrong IP returned: a stale record or a split-DNS mismatch (internal view vs external view).

## Stale Records After a Server Move
When a server changes IP address, clients may keep the old address until the record's TTL (time to live) expires. Check the TTL in the `dig` output. To speed things up:
1. Confirm the A record was updated on the authoritative server.
2. Clear the cache on the internal DNS servers for that name.
3. Ask users to flush their local cache: `ipconfig /flushdns` on Windows, `sudo dscacheutil -flushcache` on macOS.
Best practice: lower the TTL to 300 seconds at least 24 hours before a planned IP change.

## Split DNS Problems
Some names resolve to an internal address on campus and a public address off campus. If a user on VPN gets the public address, check that the VPN client is using internal DNS servers.

## Escalation
Changes to DNS zones on production servers require a standard change for single record updates and a normal change for zone or forwarder changes.
