# Tailscadble

Tailscadble is an unofficial Android/LineageOS patch set that lets the existing
`adbd` accept already-authorized ADB hosts through the installed Tailscale Android
VPN. The listener is bound to the active Tailscale VPN interface's numeric IPv4
address and is never advertised with mDNS.

This patch set does not include a remote daemon, relay, control-plane client,
remote flashing, Tailscale source code, credentials, pairing codes, host keys, or
Android signing material. It does not replace Android Wireless Debugging pairing.
It reuses ordinary `adbd` host authorization; an unapproved host remains
unauthorized.

Tailscadble is unofficial and is not affiliated with or endorsed by Tailscale
Inc. Do not use Tailscale logos or imply official support.

## Exact patch boundary

| Patch | AOSP project | Purpose |
| --- | --- | --- |
| `0001-adb-specific-listener.patch` | `packages/modules/adb` | Numeric-address bind, address-log redaction, and no mDNS for a host-bound listener |
| `0002-frameworks-base-tailscadble.patch` | `frameworks/base` | State owner, Tailscale VPN/interface validation, fail-closed lifecycle, and internal VPN-config access |
| `0003-settings-tailscadble.patch` | `packages/apps/Settings` | System-user-only Developer Options switch and explicit confirmation |
| `0004-sepolicy-listen-property.patch` | `system/sepolicy` | Allows only `init`/`system_server` to set the existing listener property type |

Validated source anchors:

- `frameworks/base`: `aaa4284f7e061771afb58c789924397111487e62`
- `packages/apps/Settings`: `adf61c13902a2789c965e6d74de5c466f5603b55`
- `packages/modules/adb`: `262cc9ada912c17f30f3130ae22e8012be4e10fe`
- `system/sepolicy`: `885cc500f6078a766d1f6def5ce4c06c55841773`

Other revisions may need a normal three-way rebase and renewed security review.

## Install into source

From an Android source root, first check all four patches against clean indexes:

```text
git -C packages/modules/adb apply --check --cached <export>/patches/0001-adb-specific-listener.patch
git -C frameworks/base apply --check --cached <export>/patches/0002-frameworks-base-tailscadble.patch
git -C packages/apps/Settings apply --check --cached <export>/patches/0003-settings-tailscadble.patch
git -C system/sepolicy apply --check --cached <export>/patches/0004-sepolicy-listen-property.patch
```

Apply the same files without `--check --cached`, then use the ROM project's normal
reviewed build and release-signing pipeline. This export intentionally contains no
build, image-repacking, AVB, staging, flashing, or release automation.

Run the host-only export checks with:

```text
python verify_export.py
python verify_export.py --source-root <android-source-root>
```

## Activate

1. Install a trusted Tailscale Android client whose package is
   `com.tailscale.ipn`, sign in, and bring its VPN up.
2. Enable Android Developer Options and USB debugging.
3. Open Developer Options, enable **Tailscadble**, and accept the warning.
4. Approve the connecting ADB host through Android's existing authorization UI.

No node address, tailnet name, pairing code, or host key is displayed or persisted
to disk by Tailscadble. While active, the exact address is held only in the
non-persistent listener property required by `adbd` and is cleared on close.

## Validation status

The predecessor OSverflow cellular-debugging implementation completed
physical-device acceptance on a release-key Lyriq build on 2026-08-29. The
recorded run proved a normal boot and expected runtime identity, a
cellular-backed Tailscale VPN, one exact Tailscale-IPv4 TCP 5555 listener with
no wildcard listener, immediate OFF closure, ON rebinding, remote Tailscale
ADB, continuing USB ADB, and no relevant fatal crash or `CONTROL_VPN`
rejection. A screenshot capture through the remote ADB path also completed
without an error.

This export is therefore not a host-only proof of concept. It does include
post-acceptance hardening that was not present in that exact device image:
address-log redaction, fail-closed observer/callback/property/restart handling,
and stricter reboot and Android-user transition resets. Those deltas need a
focused regression on a build made from these exact patches before describing
the complete export revision as device-tested. That qualification does not
erase the completed physical acceptance of the core feature. See
`TEST_PLAN.md` for the split.

## Disable, revoke, and recover

- Turn **Tailscadble** off to clear the listener and restart/stop `adbd` as needed.
- Turning off Developer Options or USB debugging also closes it. USB debugging
  must then be re-enabled and Tailscadble explicitly enabled again.
- **Revoke USB debugging authorizations** clears the Tailscadble request and the
  listener before Android removes authorized host keys.
- Tailscale VPN loss, logout, interface loss, or replacement by another VPN closes
  the listener. A later valid Tailscale reconnection may re-arm it only while the
  owner's request remains on.
- Switching away from Android's system user clears the request. Returning to the
  system user requires explicit re-enablement.
- Reboot or `system_server` reconstruction clears the request and listener. The
  system user must explicitly enable Tailscadble again.
- If UI state is uncertain, use local device UI to turn off Tailscadble, USB
  debugging, and Tailscale, then reboot. No network recovery path is assumed.

To remove the source integration, reverse the four patches in reverse order and
rebuild through the normal trusted pipeline. This document intentionally gives no
device flashing procedure.

## Security limits

- Only Android's system user can enable the feature. Headless-system-user and
  secondary-user deployments are intentionally unsupported.
- The device lock screen does not revoke an already-authorized ADB host; this
  matches existing `adbd` authorization semantics. Disable Tailscadble when that
  policy is unacceptable.
- The patch supports Tailscale IPv4 in `100.64.0.0/10`. It verifies both the VPN
  owner package and the currently active VPN interface because that CGNAT range is
  not unique to Tailscale.
- Tailscale control-plane revocation is not queried. Remote reachability after a
  node revoke remains Tailscale's control; the device test plan must prove that
  access is removed without recording addresses or keys.
- Existing physical-device evidence covers the core listener and lifecycle path.
  Host checks cover the public export itself; see `TEST_PLAN.md` for the remaining
  post-acceptance-delta regression.
