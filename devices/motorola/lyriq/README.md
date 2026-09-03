# Motorola Edge 40 (`lyriq`)

OSverflow's first support target is the Motorola Edge 40 XT2303-2 with stock
firmware baseline `V1TLS35.73-60-3-14` and an unlocked bootloader.

Current status: **release candidate**. Two XT2303-2 units accepted the frozen RC1
through recorded slot and full Virtual A/B update flows. This repository does not
yet contain a public first-install image or authorize bootloader relocking.

Validated areas on the recorded build include boot, display/high refresh, UDFPS,
DT2W, Wi-Fi, Bluetooth, NFC, GNSS, sensors, haptics, camera, audio, microphone,
cellular service on the accepted carrier path, USB, Qi with correct alignment,
local A/B updating, and the OSverflow policy features listed in
[`docs/FEATURES.md`](../../../docs/FEATURES.md).

See [installation boundary](INSTALL.md) and [known issues](KNOWN_ISSUES.md).
