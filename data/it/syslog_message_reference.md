# Network Syslog Message Reference

Document ID: NET-REF-001 | Area: Campus Network | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Explanations are general; check vendor documentation for your platform.

## How to Read a Syslog Message
Format: `%FACILITY-SEVERITY-MNEMONIC: description`. Severity 0 is the most severe (emergency) and 7 is debugging. Severity 0 to 3 messages page the on-call engineer; 4 to 7 are reviewed in the daily log report.

## Interface and Port Messages
- %LINK-3-UPDOWN: an interface changed state to up or down. Many messages for the same port in a short time indicate a flapping link; check the cable and device (NET-RB-101).
- %LINEPROTO-5-UPDOWN: the line protocol on an interface changed state. Usually follows a LINK message.
- %PM-4-ERR_DISABLE: the port manager put a port in err-disabled state. The message includes the reason, such as bpduguard or psecure-violation. Follow the err-disabled steps in NET-RB-101.
- %SPANTREE-2-BLOCK_BPDUGUARD: a BPDU was received on a port with BPDU guard enabled, so the port was disabled. Someone likely connected a switch to a user port.
- %PORT_SECURITY-2-PSECURE_VIOLATION: more MAC addresses were seen on a port than allowed by port security.

## Routing Messages
- %OSPF-5-ADJCHG: an OSPF neighbor changed state. A neighbor going from FULL to DOWN on a core link is a P1 or P2 depending on redundancy. Check the physical link and recent changes.
- %BGP-5-ADJCHANGE: a BGP neighbor went up or down. For the internet edge, a BGP neighbor down with no redundancy is a P1.

## System Messages
- %SYS-5-CONFIG_I: the configuration was changed from the CLI. The message includes the username and source IP. Compare against approved changes.
- %SYS-2-MALLOCFAIL: the device failed to allocate memory. Capture `show memory statistics` and `show processes memory sorted`, then open a vendor case; a reload may be needed in a maintenance window.
- %ENVMON-2-FAN_FAILED (or similar environment messages): a fan or power supply failed. Open a hardware replacement case; check the second power supply is healthy.
