# Sandboxed Google Play compatibility

This package carries the Android platform adaptations used to run GrapheneOS
GmsCompat as an ordinary, unprivileged app on the pinned LineageOS 23.2 source
snapshot. It is upstream-derived work, not an OSverflow invention.

The 15 platform patches are rebased onto the exact clean project revisions in
[`manifest.json`](manifest.json). The final patch adapts the public VoltageOS
GmsCompat source to the LineageOS product without its GrapheneOS LogViewer
dependency. Apply one patch in each named project; the numeric order is the
cross-project review order rather than a Git dependency between repositories.

Companion inputs are public and pinned instead of copied here:

- `packages/apps/GmsCompat`: VoltageOS commit
  `ec541b9f7ff42faad5aa553e4bb255014aec2527`, then apply
  `0016-gmscompat-app-lineage-adapter.patch`;
- `external/GmsCompatConfig`: GrapheneOS commit
  `87b8bc336cc6aca7fe480cfcc98aaaeecfd7eb6a` (version 170);
- `packages/apps/AppCompatConfig`: GrapheneOS commit
  `4bcc537aea249d2caf16c5f0425437dde175f979`, providing the
  `app_compat_config_proto-src` build input consumed by `frameworks/base`.

The recorded GmsCompatConfig APK has SHA-256
`1cab0f533caefcbf49c7c9de1b4399b3b518a5e4c91ca98c4c7cf4fd363d986d`
and GrapheneOS certificate SHA-256
`6ebb65c5daa95641f7a774ea35d26ff251575cb32e34a8a5d655b2742b57321f`.
Those values identify the upstream public prebuilt; they are not OSverflow
signing material.

## Boundary

Included: the compatibility framework, permission/package state, Binder,
runtime, connectivity, Bluetooth, NFC, AppSearch, StatsD, download, Settings,
and upstream GmsCompat app integration.

Excluded: Play Integrity verdict manipulation, build/signature/SPL spoofing,
PIF, TrickyStore, keyboxes, private-key import, certificate generation or
replacement, and the private Spacewar/Lyriq integrity experiments.

CraftedG remains a separate default-deny reference. This package does not claim
that CraftedG is integrated or device-accepted.

Preserve the upstream Android Apache-2.0 notices and the GrapheneOS MIT license
in [`LICENSE.grapheneos-gmscompat`](LICENSE.grapheneos-gmscompat).
