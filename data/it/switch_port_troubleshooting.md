# Switch Port Troubleshooting Runbook

Document ID: NET-RB-101 | Area: Campus Network | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Scope
Use this runbook when a user, printer, phone, or access point connected to an access switch has no network connectivity or poor performance. Commands shown use Cisco IOS syntax.

## Step 1: Identify the Port
1. Get the wall jack ID from the user or ticket and look up the switch and port in the cabling database.
2. Confirm with the MAC address if the device is known:
```
show mac address-table address <mac>
```
3. Check port status:
```
show interfaces status | include <port>
```

## Port Status: notconnect
The switch sees no link. Likely causes: unplugged or damaged patch cable, bad wall jack, device powered off, or NIC disabled.
Actions: ask the user to reseat the cable, test with a known-good cable, and if needed dispatch a technician with a cable tester. If the device is PoE powered (phone or AP), check `show power inline <port>`.

## Port Status: err-disabled
The switch shut the port down because of a policy violation. Find the reason first:
```
show interfaces status err-disabled
show errdisable recovery
```
Common reasons:
- bpduguard: someone connected a switch or a device that sends BPDUs to a user port. Remove the device before re-enabling the port.
- psecure-violation: port security saw more MAC addresses than allowed (often a small unmanaged switch under a desk).
- link-flap: the link went up and down too many times; check the cable and the device NIC.

To re-enable the port after the cause is removed:
```
configure terminal
interface <port>
shutdown
no shutdown
end
```
Re-enabling a port on a production switch is a standard change; record it in the ticket. Do not disable bpduguard to make the problem go away.

## Port Is Up but Device Has No Network
1. Check the access VLAN matches the jack's intended VLAN: `show interfaces <port> switchport`.
2. A data VLAN of 1 or a wrong VLAN usually means the port was never configured or was reset to defaults.
3. For phones, confirm the voice VLAN is set.
4. If the VLAN is correct, continue with the DHCP runbook (NET-RB-102).

## Slow Performance or Errors
Check interface counters:
```
show interfaces <port> | include errors|duplex|CRC
```
- Rising CRC or input errors usually mean a bad cable or jack.
- Half duplex or a 10/100 speed on a gigabit device usually means a duplex mismatch or a damaged cable pair. Set both sides to auto-negotiate.
Clear counters with `clear counters <port>` and check again after 10 minutes to confirm the errors are still increasing.

## Escalation
Escalate to Network Engineering (Tier 2) if more than one port on the same switch is affected, if the uplink is down, or if the switch is unreachable.
