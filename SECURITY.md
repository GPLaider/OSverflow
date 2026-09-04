# Security policy

## Supported security scope

The public tree is currently a source release candidate. No public installable
OSverflow build is designated as a stable security release.

Report vulnerabilities through a private GitHub Security Advisory after the
repository is published. Do not attach device identifiers, subscriber data,
Tailscale addresses, ADB keys, activation codes, signing keys, keyboxes, private
certificates, or unredacted logs to a public issue.

## Product limits

- The device-accepted Lyriq RC1 is `userdebug`. A separate production `user`
  candidate passed static artifact checks but has not passed device acceptance.
  Both require an unlocked bootloader.
- Bootloader relocking is unsupported.
- Cellular, wireless, or USB debugging must be disabled when not required.
- Tailscadble does not bypass Android ADB host authorization.
- CraftedG makes no Play Integrity or attestation-verdict claim.
- Camera, microphone, location, call, and SMS controls are software policy
  boundaries; they are not physical disconnect switches.
- The frozen device-accepted RC1 framework SPL is `2026-06-01`. The production
  candidate reports `2026-08-01`, but OSverflow does not claim current bulletin
  coverage until the patch-integration gate in `RELEASE_CHECKLIST.md` is closed.

Release signing, OTA signing, APK signing, and AVB signing are separate trust
domains. Never infer one from another or publish private material from any of
them.
