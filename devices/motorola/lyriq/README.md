# Motorola Edge 40 (`lyriq`)

OSverflow's first support target is the Motorola Edge 40 XT2303-2 with stock
firmware baseline `V1TLS35.73-60-3-14` and an unlocked bootloader.

The sanitized device integration is maintained separately in
[`android_device_motorola_lyriq`](https://github.com/GPLaider/android_device_motorola_lyriq).
It pins independent input contracts for the frozen RC1 hardware source
(`V1TLS35.73-60-3-10` / `40dcc-72d036`) and the first-install baseline under
review (`V1TLS35.73-60-3-14` / `89e5f-45c91`). Extraction is verified for both;
physical first-install acceptance remains a release blocker.

The public GKI identity and five matching Motorola kernel-source repositories,
including Lyriq DTS and hardware drivers, are pinned in the device repository.
Vendor/external module revision and reproducible-build closure remain open.

Current status: **release candidate**. Two XT2303-2 units accepted the frozen RC1
through recorded slot and full Virtual A/B update flows. This repository does not
yet contain a public first-install image or authorize bootloader relocking.

Validated areas on the recorded build include boot, display/high refresh, UDFPS,
DT2W, Wi-Fi, Bluetooth, NFC, GNSS, sensors, haptics, camera, audio, microphone,
cellular service on the accepted carrier path, USB, Qi with correct alignment,
local A/B updating, and the OSverflow policy features listed in
[`docs/FEATURES.md`](../../../docs/FEATURES.md).

See [installation boundary](INSTALL.md) and [known issues](KNOWN_ISSUES.md).
