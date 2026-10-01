# Network Configuration Backup Runbook

Document ID: NET-RB-110 | Area: Network Automation | Owner: Network Operations
Note: Fictional sample document created for a portfolio project ("Example Org"). Not a real organization's procedure.

## How Backups Work
A Python job runs nightly at 01:00 and logs into every device in the inventory over SSH, runs `show running-config`, and commits the output to the configuration Git repository (one file per device). A summary report is emailed to the network operations mailbox at 06:00 with any failed devices.

## Failure: Authentication Failed
Report shows `AuthenticationException` for one or more devices.
Likely causes:
- The service account password was rotated but the backup job's credential vault entry was not updated.
- The device is not using central authentication (TACACS+) and the local account is missing.
- The device was replaced and the new device has default credentials.
Actions:
1. Test a manual SSH login to the device with the service account.
2. If all devices fail, update the credential in the vault and rerun the job.
3. If one device fails, check `show running-config | include aaa|username` on the device.

## Failure: Timeout
Report shows `NetmikoTimeoutException` or `connection timed out`.
Likely causes: the device is down, the management ACL does not allow the backup server's IP, or the device is reachable only from the management VRF.
Actions: ping the device management IP from the backup server, confirm the backup server IP is in the management ACL, and confirm the inventory entry uses the management IP.

## Failure: Device Missing From Report
New devices are only backed up after they are added to the inventory file `inventory/devices.yaml`. Add the device with hostname, management IP, platform, and site, then open a pull request for review.

## Config Change Alerts
If the nightly diff shows changes on a device with no approved change ticket, treat it as an unauthorized change: check the device logs for `%SYS-5-CONFIG_I` to find who made it and when, and notify the network manager.

## Restoring a Configuration
1. Find the last known-good version in the Git history for that device.
2. Open an emergency or normal change, depending on impact.
3. Apply only the needed lines, not the whole file, unless the device was replaced.
4. Save with `write memory` and confirm the next nightly backup shows the expected config.
