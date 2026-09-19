# Release model

OSverflow uses Android's native full Virtual A/B and UpdateEngine flow. It does
not add a second updater, a background remote-flashing daemon, or a public ADB
relay.

Every candidate has four independent acceptance layers:

1. source and unit checks;
2. built-module signer and identity checks;
3. extracted partition, AVB, OTA, and payload checks;
4. physical-device behavior and rollback checks.

A candidate advances only when all applicable layers pass. `release-keys` text,
a successful build, or a boot animation is not release acceptance.

The Lyriq `userdebug` candidate OSVLYRIQ1 passed all four layers: static
target-files, signer, AVB, extracted-partition, and OTA-payload checks, plus
physical-device acceptance on two units (slot B, userdata preserved, root ADB,
Enforcing). A public first-install package ships five OSverflow-owned images
(product, system, system_ext, vbmeta, vbmeta_system) against the
V1TLS35.73-60-3-14 stock contract and is described in
devices/motorola/lyriq/RELEASE_NOTES-OSVLYRIQ1.md. The stock-to-OSverflow
first-install wipe path and end-to-end inactive-slot OTA installation are still
not exercised on third-party hardware. No public OTA endpoint is declared until
its signed metadata, artifact retention, rollback policy, and key custody are
reviewed.
