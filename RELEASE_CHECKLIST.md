# Public release checklist

## Source RC — required before repository publication

- [x] Tailscadble export verifier passes.
- [x] Upstream-derived GmsCompat platform patches are rebased onto exact clean
      Lineage project anchors; integrity/key/certificate experiments are excluded.
- [x] CraftedG JDK 17 compile and assertion test pass.
- [x] Reusable privacy, call, and SMS patches are separated from the dirty ROM tree.
- [x] Feature and Lyriq status distinguish device acceptance from export validation.
- [x] Secret/binary/path scan passes on tracked candidates.
- [ ] Repository visibility and public description selected by the maintainer.
- [x] Android project integrations are replayable from their pinned upstreams.
- [x] Lyriq clean-checkout manifest and six device-specific platform-support
      patches are pinned, hash-verified, and replayable at exact source anchors.
- [x] Sanitized Lyriq device-source candidate is isolated and CI-verified.
- [x] CraftedG remains intentionally isolated from the mixed private Android
      integration until a clean default-deny port exists.
- [x] Current source-RC SPDX/NOTICE review completed and enforced by the verifier.

## Installable Lyriq release — additional blockers

- [x] Package the accepted source deltas as clean, exact-anchor patchsets.
- [x] Reconstruct those patchsets in a separate clean Android checkout and pass
      the `osverflow_lyriq-bp4a-user` Soong/Make graph preflight.
- [x] Pin the exact public GKI identity and five matching Motorola kernel-source
      repositories, including Lyriq DTS and hardware drivers.
- [ ] Resolve and reproduce the missing kernel/vendor-module sources, or close
      the corresponding-source and lawful-prebuilt redistribution path before
      publishing any installable binary.
- [x] User-supplied stock-firmware extraction is hash-pinned and verified for
      exact `-3-10` and `-3-14` contracts without redistributing payloads.
- [x] The complete 27-file stock IMS input contract is hash-pinned, extracted
      locally, and bound to the production source gate.
- [x] F-Droid Classic and GrapheneOS App Store inputs are pinned to exact
      upstream APK and signer identities without redistributing the APKs.
- [ ] Integrate and validate a current Android security bulletin without changing
      the date by property alone.
- [x] Preflight the private production signer map for every APK role and every
      signable APEX container/payload key while preserving upstream-signed APKs.
- [x] Produce a production `user` build and statically validate its target-files
      signing, APK/APEX signers, AVB chain, partition identity, and OTA payload.
- [ ] Pass physical-device boot, runtime, and rollback acceptance for that exact
      production candidate.
- [ ] Qualify a clean first install from the declared Motorola stock baseline on
      the spare XT2303-2, including recovery and rollback.
- [ ] Re-run the exact Tailscadble hardening export matrix on a signed device build.
- [ ] Close or explicitly document carrier, accessory, and regional test gaps.
- [ ] Publish checksums, public trust anchors, release notes, install instructions,
      and rollback instructions with the exact uploaded artifact.

Until every installable-release item is closed, do not upload the internal OTA as
a public stable release.
