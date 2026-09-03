# OSverflow security suite 0/5/6/7/8

The accepted Lyriq sequence was deliberately built in this order:

| Number | Feature | Implementation |
| ---: | --- | --- |
| 0 | Verified Update + A/B rollback | Native AOSP UpdateEngine and full Virtual A/B OTA, with an explicit release certificate and independently verified AVB graph |
| 5 | USB data restriction | Existing Lineage Trust `trust_restrict_usb`; no duplicate OSverflow service |
| 6 | Inactivity reboot to BFU | Alarm/keyguard policy service plus one LineageParts list preference |
| 7 | Disposable Space | Android full guest forced ephemeral by resource overlay; no custom deletion code |
| 8 | Compatibility Profiles | AVB-protected, exact package/signer/version/expiry-scoped PlatformCompat catalog; empty by default |

## Export status

Features 0 and 5 are documented native/upstream reuse. Feature 6 includes clean
framework and LineageParts patches with its policy test. Feature 7 includes the
exact minimal device-overlay recipe. Feature 8 includes clean framework and
Settings patches with its parser, service, Android test, read-only UI, and an
empty device catalog.

The Android project patches are independently replayable at their exact source
anchors. The Lyriq device overlay is still a merge recipe because that device
tree is not yet under clean public Git history. A downstream release must also
run the full build, signer, partition, AVB, OTA, and device acceptance matrix.

## Source anchors

- `frameworks/base`: `aaa4284f7e061771afb58c789924397111487e62`
- `packages/apps/Settings`: `adf61c13902a2789c965e6d74de5c466f5603b55`
- `packages/apps/LineageParts`: `df5dd9d53b01553168fd9c57e5c6b8bc8b4550c7`
- Lyriq device overlay: deterministic recipe, but still awaiting a clean public
  device-tree anchor

## Security invariants

- Inactivity reboot starts unarmed after boot, arms only after AFU plus secure
  lock, accepts only whitelisted timeouts, cancels on unlock, and rechecks state
  at expiry.
- Disposable Space is a forced-ephemeral Android guest; leaving the guest invokes
  Android's native user/key/data teardown.
- Compatibility Profiles read only `/system/etc/osverflow/` data covered by the
  system AVB chain. Every active entry requires exact package, signer, inclusive
  version range, finite expiry, reason, security impact, and owned change IDs.
- The production profile catalog is empty. No compatibility weakening is
  invented in advance and no global disable switch exists.
