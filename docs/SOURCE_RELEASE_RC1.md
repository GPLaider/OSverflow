# OSverflow 16 source RC1

Status: source-only release candidate. No installable ROM is attached.

This release packages the reviewable OSverflow work for Android 16:

- Tailscadble's four exact-anchor ADB/VPN policy patches, threat model, tests,
  and verifier;
- the attributed GrapheneOS-derived sandboxed Google Play compatibility patch
  series;
- CraftedG's independent default-deny stock-KeyStore delegation reference;
- Privacy Lock, independent call/SMS controls, Security Suite 0/5/6/7/8, and
  Lyriq platform-support patchsets;
- the pinned clean-checkout manifest and support contract for Motorola Edge 40
  XT2303-2 (`lyriq`), OSverflow's first support target.

Run `python verify_release.py` with Python 3.11+ and JDK 17+. A valid checkout
ends with `OSVERFLOW_RELEASE_SOURCE_OK`. Maintainers with the pinned Android
source may also run `tools/verify_android_patches.sh` in dry-run, apply, or
check-applied mode as documented in the root README.

The private production `user` candidate passed static target-files, actual
APK/APEX signer, AVB-chain, extracted-partition, and OTA-payload equality checks.
It has not passed physical-device boot, runtime, first-install, or rollback
acceptance and is not a public download.

Excluded from this source release are proprietary Motorola/MediaTek payloads,
ROM and AVB private keys, signing material, device or subscriber identifiers,
Tailscale identity, ADB host keys, eSIM activation data, keyboxes, Play Integrity
verdict manipulation, certificate replacement, and every private ROM binary.

See `RELEASE_CHECKLIST.md`, `SECURITY.md`, and
`devices/motorola/lyriq/KNOWN_ISSUES.md` before treating any component as ready
for production use.
