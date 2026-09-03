# Public release checklist

## Source RC — required before repository publication

- [x] Tailscadble export verifier passes.
- [x] CraftedG JDK 17 compile and assertion test pass.
- [x] Reusable privacy, call, and SMS patches are separated from the dirty ROM tree.
- [x] Feature and Lyriq status distinguish device acceptance from export validation.
- [x] Secret/binary/path scan passes on tracked candidates.
- [ ] Repository visibility and public description selected by the maintainer.
- [ ] Remaining reference-only integrations converted to clean replayable commits.
- [x] Current source-RC SPDX/NOTICE review completed and enforced by the verifier.

## Installable Lyriq release — additional blockers

- [ ] Reconstruct the accepted source as clean per-project Git commits.
- [ ] Publish the corresponding kernel source and complete source manifest.
- [ ] Resolve Motorola/MediaTek proprietary redistribution permissions or require
      users to extract legally obtained stock firmware.
- [ ] Integrate and validate a current Android security bulletin without changing
      the date by property alone.
- [ ] Produce and validate a production `user` build.
- [ ] Qualify a clean first install from the declared Motorola stock baseline on
      the spare XT2303-2, including recovery and rollback.
- [ ] Re-run the exact Tailscadble hardening export matrix on a signed device build.
- [ ] Close or explicitly document carrier, accessory, and regional test gaps.
- [ ] Publish checksums, public trust anchors, release notes, install instructions,
      and rollback instructions with the exact uploaded artifact.

Until every installable-release item is closed, do not upload the internal OTA as
a public stable release.
