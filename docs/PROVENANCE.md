# Provenance and redistribution boundary

OSverflow combines AOSP and LineageOS platform work with independently authored
OSverflow changes and device integration. The private experimental build also
uses legally obtained Motorola/MediaTek firmware and vendor components.

This repository distributes no proprietary partition image or ROM binary. A
future public device build must either have a documented right to redistribute
each proprietary payload or provide a reproducible extractor that consumes the
user's legally obtained stock firmware.

The sanitized Lyriq integration and its hash-only local-input contracts live in
[`android_device_motorola_lyriq`](https://github.com/GPLaider/android_device_motorola_lyriq).
It contains no proprietary payload and does not claim exact kernel-source closure.
Its extractor was accepted against exact `V1TLS35.73-60-3-10` and
`V1TLS35.73-60-3-14` Software Fix packages and rejects other builds before
creating output. That repository also pins the exact public GKI release identity
and five Motorola `v1tl35.73-60-3` source repositories while explicitly keeping
unresolved vendor/external kernel modules outside reproducible-build claims.

Feature directories contain their own source anchors and attribution where the
boundary differs. Branding never erases upstream authorship, copyright, license,
or trademark obligations.

The Lyriq clean-checkout recipe is pinned by
`devices/motorola/lyriq/local_manifests/osverflow-lyriq.xml`. Device-specific
Android deltas that are not reusable OSverflow features are isolated under
`features/lyriq-platform-support/`; its manifest binds every patch to an exact
project base and hash.
