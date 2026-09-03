# Integration points

## Feature 6: inactivity reboot

Copy `InactivityRebootService.java` into `frameworks/base/services/core` and call
it once from the ROM's existing system-server extension point after required
services exist, on a background handler:

```java
InactivityRebootService.init(systemContext, backgroundHandler);
```

Apply `0001-lineageparts-inactivity-reboot-ui.patch` to the anchored LineageParts
tree. Preserve the setting key and timeout whitelist.

## Feature 7: Disposable Space

Merge the files in `reference/device/motorola/lyriq/overlay/` into the device's
framework resource overlay. Do not add manual deletion code.

## Feature 8: Compatibility Profiles

Copy the parser, test, Settings fragment, and empty catalog to their matching
paths. Apply the service and gateway patches, then merge the Settings resource
fragments. Product makefiles must install the catalog at
`/system/etc/osverflow/compatibility_profiles.properties` as root-owned `0644`
`system_file` data.

The service must start after PlatformCompat is available, reconcile on package
and DeviceConfig changes, reject ownership collisions, and remove expired or
retired owned overrides. A downstream build that changes these semantics needs
its own threat review.
