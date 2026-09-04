# OSverflow

OSverflow is an independent Android platform project derived from AOSP and
LineageOS. The first supported target is the Motorola Edge 40
(`lyriq`, XT2303-2).

This repository is a **source release candidate**, not an installable public ROM
release. It packages the independently reviewable OSverflow features, their trust
boundaries, and the first device support contract. The accepted Lyriq RC1 binary
is deliberately not tracked while first-install qualification, complete source
and notice closure, current security-patch integration, `user` build conversion,
and proprietary redistribution review remain open.

## Included source packages

| Component | Public status | What is here |
| --- | --- | --- |
| [Tailscadble](features/tailscadble/README.md) | patch export | Four anchored Android patches, threat model, test plan, host verifier |
| [Sandboxed Google Play compatibility](features/gmscompat/README.md) | upstream-derived patch export | Fifteen platform adaptations, one Lineage app adapter, and pinned public GrapheneOS config input |
| [CraftedG](features/craftedg/README.md) | host reference | Default-deny, process-scoped stock KeyStore delegation; no verdict or certificate manipulation |
| [Privacy Lock](features/privacy-lock/README.md) | patch export | Framework service gates for camera, microphone, and location locks |
| [Cellular Service Controls](features/cellular-service-controls/README.md) | patch export | Independent call and SMS gates plus Settings UI while cellular data stays provisioned |
| [Security Suite 0/5/6/7/8](features/security-suite-05678/README.md) | patch + device recipe | Verified-update model, USB restriction reuse, inactivity reboot, Disposable Space, compatibility profiles |
| [Lyriq platform support](features/lyriq-platform-support/README.md) | source-closure patchset | Six pinned hybrid-build, SELinux, IMS, and vendor-visibility patches |

See [feature status](docs/FEATURES.md), [release model](docs/RELEASE_MODEL.md),
[source RC1 notes](docs/SOURCE_RELEASE_RC1.md),
[license audit](docs/LICENSE_AUDIT.md), [Lyriq support](devices/motorola/lyriq/README.md),
and the separate
[`android_device_motorola_lyriq`](https://github.com/GPLaider/android_device_motorola_lyriq)
source candidate before reusing anything.

## Verify this source export

Requires Python 3.11+ and JDK 17+:

```text
python verify_release.py
```

Expected final line:

```text
OSVERFLOW_RELEASE_SOURCE_OK
```

Maintainers with the exact Android source anchors may additionally run:

```text
tools/verify_android_patches.sh <android-source-root>
```

Expected final line: `OSVERFLOW_ANDROID_PATCHES_OK`.

After that dry-run succeeds on a clean checkout, apply the identical verified
series in place with:

```text
tools/verify_android_patches.sh --apply <android-source-root>
```

This refuses dirty project inputs, stages every patch, and accepts only the
expected 27 modified Android projects. Expected final line:
`OSVERFLOW_ANDROID_PATCHES_APPLIED_OK`.

The same exact-tree postcondition can be rerun later without modifying source:

```text
tools/verify_android_patches.sh --check-applied <android-source-root>
```

Expected final line: `OSVERFLOW_ANDROID_PATCHES_MATCH_OK`.

## Current Lyriq anchors

- Device-accepted private RC1: `userdebug`, framework SPL `2026-06-01`, vendor SPL
  `2026-08-01`; OTA SHA-256:
  `2bac3971baefa5aeb01595744d18ffb9648dd3f069866d39213d134e97f1a836`
- Production candidate: `osverflow_lyriq-bp4a-user`, Android 16 / SDK 36,
  framework and vendor SPL `2026-08-01`; fingerprint
  `motorola/osverflow_lyriq/lyriq:16/BP4A.251205.006/OSVLYRIQRC1:user/release-keys`.
- The production candidate passed target-files signing, actual APK/APEX signer,
  AVB-chain, extracted-partition identity, and OTA-payload equality checks. OTA
  SHA-256: `740d3a5896845116a02d3b70a323d87413dc4118f159a5849eef5c484d5eb502`.
- Public install artifact: none. The production candidate has not been flashed
  or accepted on a physical device, and the remaining public-binary gates still
  apply.

The hashes identify private maintainer evidence; they are not download promises
or permission to redistribute either binary.

## Independence

OSverflow is not an official LineageOS, GrapheneOS, Motorola, Google, F-Droid,
or Tailscale product. Upstream names identify provenance or interoperability
only. Preserve upstream licenses, file headers, notices, and trademarks.
