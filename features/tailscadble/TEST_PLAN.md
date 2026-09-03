# Tailscadble verification plan

Never save a tailnet name, node address, user IP, pairing code, ADB host key, auth or
node key, or Android signing key in test output. Inspect address-bearing live state
locally, redact it before sharing, and delete transient captures.

## Host and source checks

1. Run `python verify_export.py`.
2. Run `python verify_export.py --source-root <android-source-root>` against the
   exact clean source anchors in `README.md`.
3. Require four successful `git apply --check --cached` results.
4. Run each project's normal format/lint/unit targets. At minimum, run the existing
   `socket_spec_listen_connect_tcp_specific_ipv4` test introduced by patch 0001.
5. Confirm source diffs contain only the files named in the four patches.
6. Build only through the project's trusted release process. Verify APK/APEX and
   partition identities independently; this export contains no signer assumptions.

## Recorded physical-device acceptance

Physical-device acceptance was completed for the predecessor OSverflow
cellular-debugging implementation on 2026-08-29. Private evidence is intentionally
excluded from this public source export because it contains device and network
identifiers. The recorded, redacted results are:

- normal Lyriq boot, expected release-key identity, SELinux Enforcing, and required
  Android processes alive;
- active Tailscale VPN backed by cellular data;
- TCP 5555 bound to the exact active Tailscale IPv4 address, with no wildcard
  listener;
- setting OFF removed every TCP 5555 listener, and setting ON rebound the exact
  listener;
- remote ADB through Tailscale and wired USB ADB both worked;
- the post-boot log check found no repeated `CONTROL_VPN` rejection or relevant
  fatal crash; and
- a remote screenshot capture completed with empty stderr.

The run ended with `OSVERFLOW_CELLULAR_LIFECYCLE_OK` and
`OSVERFLOW_V42_RUNTIME_OK`. This is completed real-device functional acceptance,
not a host-model substitute.

## Exact-export regression matrix

The public export adds hardening after that accepted build. All future device work
still requires separate authorization. Re-run the applicable rows below on a signed
build made from these exact patches; give priority to rows exercising address-log
redaction, fail-closed errors, reboot reset, and Android-user transitions.

| Case | Action | Required result |
| --- | --- | --- |
| Stock OFF | Fresh boot with setting absent | no TCP listener; property empty; USB behavior unchanged |
| Explicit ON | System user enables USB debugging, Tailscale VPN, then Tailscadble | warning shown; one exact VPN-address listener; no mDNS record |
| Unapproved host | Connect from a fresh host with no approved ADB key | host remains unauthorized; shell unavailable |
| Approved host | Approve through Android's normal prompt | shell works only over the validated tailnet path |
| Tailnet-only | Probe from tailnet, LAN/Wi-Fi address, carrier address, and public path | only approved tailnet path reaches adbd |
| Toggle OFF | Disable Tailscadble during an active session | listener closes immediately; reconnect fails |
| USB OFF | Disable USB debugging | request and listener clear; re-enabling USB alone does not reopen |
| Authorization revoke | Use Android's revoke-debugging-authorizations UI | listener closes and old host cannot reconnect |
| Tailscale down | Stop the VPN while active | listener closes; USB ADB remains according to stock setting |
| Tailscale logout/node revoke | Logout or revoke without recording identifiers | remote reachability ends; no stale listener path is usable |
| VPN replacement | Replace Tailscale with another VPN, including one using CGNAT | listener closes and stays closed |
| User switch | Switch to a secondary/guest user | request clears before that user can inherit access |
| Return to owner | Switch back to system user | listener stays off until explicit ON |
| Wi-Fi to cellular | Transition while connected | listener never appears on Wi-Fi/carrier address; validated Tailscale path recovers |
| Cellular to Wi-Fi | Reverse transition | same invariant |
| Device lock | Lock/unlock during an authorized session | documented stock ADB authorization behavior; no new unauthenticated access |
| Doze | Enter/exit Doze, then drop/restore VPN | drop closes reachability; restore follows requested state only |
| Reboot | Reboot with request off, then with prior request on | request/property start off; no listener until explicit owner ON |
| adbd restart | Restart adbd under ON, OFF, and VPN-loss states | exact current state restored; no wildcard or stale listener |
| system_server restart | Restart framework process in a disposable test environment | request/listener clear; USB behavior recovers; explicit owner ON is required |

## Log, privacy, and export checks

- Search Settings, system-server, init, and adbd logs for the feature tag. Status may
  say only `active` or `closed`; it must not include a runtime address or listen spec.
- Confirm the Settings summary never displays an address or tailnet name.
- Scan the final archive with the same rules as `verify_export.py`, plus the release
  project's credential scanner.
- Confirm the archive excludes build outputs, images, APK/APEX files, logs, captures,
  `.git`, private configuration, and signing material.

## Release gate

Core functional acceptance is complete. This source export may be reviewed or
shared with the validation disclosure above. Do not describe the exact hardened
export revision as fully device-tested until a signed build passes the applicable
post-acceptance-delta rows, the external-call VPN permission behavior is tested,
and a human reviews the Tailscadble name/non-affiliation text for trademark risk.
