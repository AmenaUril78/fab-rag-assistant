# Network Automation Scripts Guide

Document ID: NET-AUTO-005 | Area: Network Automation | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## Overview
Network Operations uses Python scripts (Netmiko and Nornir) stored in the automation Git repository to push repeatable configuration changes, such as updating NTP servers, SNMP settings, or interface descriptions, across many devices.

## Before Running Any Script
1. Pull the latest version of the repository and work on a branch.
2. Confirm an approved change request exists for the change, or that it is a pre-approved standard change.
3. Confirm that a fresh config backup exists for every target device (NET-RB-110).
4. Always run in dry-run mode first:
```
python push_config.py --inventory inventory/devices.yaml --group building-a --dry-run
```
   Dry-run shows the commands each device would receive without applying them.

## Running a Change
1. Start with one pilot device: `--limit <hostname>`. Verify the result manually.
2. Run against the rest of the group in batches of 20 devices using `--batch-size 20`.
3. The script saves a log for each device in `logs/<date>/`. Review the summary for any failed devices.

## Common Errors
- NetmikoAuthenticationException: wrong credentials or the device does not use TACACS+. See the authentication section of NET-RB-110.
- NetmikoTimeoutException: the device is unreachable from the automation server or the management ACL blocks it.
- ReadTimeout or "Pattern not detected": the device prompt was different than expected, often because of a banner or a long command. Increase `read_timeout` for that platform or check the device prompt.
- Partial failure: some devices were changed and some were not. Do not rerun blindly; check which devices succeeded in the logs, then rerun with `--limit` for the failed ones.

## Rollback
Every push script must have a matching rollback template. Run it with the same inventory group and `--rollback`. If no rollback template exists, the change cannot be run as automation.
