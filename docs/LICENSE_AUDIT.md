# License and NOTICE audit

Scope: the OSverflow source-release candidate. The repository is licensed under
Apache License 2.0. Independently authored Java, Python, and shell sources carry
an `SPDX-License-Identifier: Apache-2.0` marker enforced by
`verify_release.py`; configuration and documentation are covered by the root
`LICENSE` and `NOTICE`.

## Patched upstream projects

| Android project | Source anchor | Upstream | License evidence |
| --- | --- | --- | --- |
| `packages/modules/adb` | `262cc9ada912c17f30f3130ae22e8012be4e10fe` | [LineageOS](https://github.com/LineageOS/android_packages_modules_adb) | Root `NOTICE`, `MODULE_LICENSE_APACHE2`, and Apache-2.0 target-file header |
| `frameworks/base` | `aaa4284f7e061771afb58c789924397111487e62` | [LineageOS](https://github.com/LineageOS/android_frameworks_base) | Root `NOTICE`, `MODULE_LICENSE_APACHE2`, and Apache-2.0 target-file headers |
| `packages/apps/Settings` | `adf61c13902a2789c965e6d74de5c466f5603b55` | [LineageOS](https://github.com/LineageOS/android_packages_apps_Settings) | Root `NOTICE` and Apache-2.0 target-file headers |
| `system/sepolicy` | `885cc500f6078a766d1f6def5ce4c06c55841773` | [LineageOS](https://github.com/LineageOS/android_system_sepolicy) | Root `NOTICE`; patch remains within that project |
| `frameworks/opt/telephony` | `21e2e9fc3cf0992bd91863aa33784ec5b24a806a` | [LineageOS](https://github.com/LineageOS/android_frameworks_opt_telephony) | Apache-2.0 target-file headers |
| `packages/services/Telephony` | `95e95093d0e9cca76b86906d414a7da6b95d45fe` | [LineageOS](https://github.com/LineageOS/android_packages_services_Telephony) | Apache-2.0 target-file headers |
| `packages/apps/LineageParts` | `df5dd9d53b01553168fd9c57e5c6b8bc8b4550c7` | [LineageOS](https://github.com/LineageOS/android_packages_apps_LineageParts) | SPDX Apache-2.0 target-file headers |
| `build/make` | `5a841be38fec92de9a8a408cf5812ca748ccc02e` | [LineageOS](https://github.com/LineageOS/android_build) | Apache-2.0 target-file headers |
| `device/lineage/sepolicy` | `c6e972cf4ff9bd472052b29cf8eae7bc3e70d378` | [LineageOS](https://github.com/LineageOS/android_device_lineage_sepolicy) | Apache-2.0 project source |
| `packages/modules/Telephony` | `6175c04a2cb3254455c58c9c653dc36a8a7e6dac` | [AOSP](https://android.googlesource.com/platform/packages/modules/Telephony/) | Apache-2.0 shim source header |
| `external/selinux` (`libsepol`) | `085c131ad1b984bfa8ffdafee7a976e9d89f403c` | [AOSP](https://android.googlesource.com/platform/external/selinux/) | LGPL-2.1 license copy included |
| `external/dng_sdk` | `60de57ba9f18dd6366914ad74580063fe102c87c` | [AOSP](https://android.googlesource.com/platform/external/dng_sdk/) | Adobe DNG SDK license copy included |
| `external/libjxl` | `4365ed52860edc6898277200c9bb41971f005e11` | [AOSP](https://android.googlesource.com/platform/external/libjxl/) | BSD-3-Clause license copy included |

Patch files contain OSverflow deltas against those exact commits. Applying a
patch does not replace upstream ownership: downstream distributions must retain
the complete license, NOTICE, and file headers from every Android project they
build.

## Independently authored components

- Tailscadble: Apache-2.0; separate `LICENSE` and `NOTICE` included.
- CraftedG: Apache-2.0; independently authored reference and tests. No third-party
  implementation was copied.
- Privacy Lock, Cellular Service Controls, and Security Suite 0/5/6/7/8:
  OSverflow additions under Apache-2.0, with upstream portions retained as
  anchored patches.
- Device metadata and integration recipes: Apache-2.0.

The Lyriq platform-support directory retains separate full license copies for
`libsepol`, DNG SDK, and JPEG XL. Its root Apache license does not replace those
upstream terms.

## Upstream-derived GmsCompat package

The GmsCompat platform adaptations are derived from GrapheneOS Android platform
work and retain Apache-2.0 project ownership and notices. The companion
GmsCompat application and configuration holder are GrapheneOS MIT-licensed work;
the exact public source/prebuilt revisions and MIT text are recorded under
`features/gmscompat/`. OSverflow claims authorship only for its narrow LineageOS
adapter and rebase, not for GmsCompat itself.

## Excluded material

No Motorola/MediaTek proprietary image, firmware, APK, signing key, keybox,
certificate payload, Tailscale source, or third-party ROM binary is distributed.
Names and marks identify provenance or interoperability only; see the root
`NOTICE` for non-affiliation statements.
