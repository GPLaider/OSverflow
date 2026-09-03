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
| [CraftedG](features/craftedg/README.md) | host reference | Default-deny, process-scoped stock KeyStore delegation; no verdict or certificate manipulation |
| [Privacy Lock](features/privacy-lock/README.md) | patch export | Framework service gates for camera, microphone, and location locks |
| [Cellular Service Controls](features/cellular-service-controls/README.md) | patch + reference | Independent call and SMS gates while cellular data stays provisioned |
| [Security Suite 0/5/6/7/8](features/security-suite-05678/README.md) | mixed export | Verified-update model, USB restriction reuse, inactivity reboot, Disposable Space, compatibility profiles |

See [feature status](docs/FEATURES.md), [release model](docs/RELEASE_MODEL.md),
and [Lyriq support](devices/motorola/lyriq/README.md) before reusing anything.

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

## Current Lyriq binary anchor

- Product: OSverflow 16 RC1
- Target: Motorola Edge 40 XT2303-2 / `lyriq`
- Android: 16 / SDK 36
- Build type: `userdebug`
- Framework SPL: `2026-06-01`
- Vendor SPL: `2026-08-01`
- Frozen internal OTA SHA-256:
  `2bac3971baefa5aeb01595744d18ffb9648dd3f069866d39213d134e97f1a836`

The hash identifies private maintainer evidence; it is not a download promise or
permission to redistribute the binary.

## Independence

OSverflow is not an official LineageOS, GrapheneOS, Motorola, Google, F-Droid,
or Tailscale product. Upstream names identify provenance or interoperability
only. Preserve upstream licenses, file headers, notices, and trademarks.
