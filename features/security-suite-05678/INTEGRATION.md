# Integration points

## Feature 6: inactivity reboot

Apply `0002-frameworks-base-inactivity-reboot.patch` to `frameworks/base` and
`0001-lineageparts-inactivity-reboot-ui.patch` to LineageParts. The framework
patch starts the service on Android's background handler at the accepted
system-ready point. Preserve the setting key and timeout whitelist.

## Feature 7: Disposable Space

Merge the files in `reference/device/motorola/lyriq/overlay/` into the device's
framework resource overlay. Do not add manual deletion code.

## Feature 8: Compatibility Profiles

Apply `0003-frameworks-base-compatibility-profiles.patch` and
`0004-settings-compatibility-profiles.patch`, then install the empty catalog at
`/system/etc/osverflow/compatibility_profiles.properties` as root-owned `0644`
`system_file` data.

The service must start after PlatformCompat is available, reconcile on package
and DeviceConfig changes, reject ownership collisions, and remove expired or
retired owned overrides. A downstream build that changes these semantics needs
its own threat review.
