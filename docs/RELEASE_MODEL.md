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

The frozen Lyriq `userdebug` RC1 was accepted as a local update on existing
compatible OSverflow installations. A separate production `user` candidate has
passed static target-files, signer, AVB, extracted-partition, and OTA-payload
checks but has not passed physical-device acceptance. A public first-install
package is a separate artifact and is not yet qualified. No public OTA endpoint
is declared until its signed metadata, artifact retention, rollback policy, and
key custody are reviewed.
