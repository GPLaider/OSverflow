#!/usr/bin/env python3
"""Host-only structural, state-machine, secret, and patch-application checks."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from ipaddress import IPv4Address
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parent
PATCHES = ROOT / "patches"
PATCH_MAP = {
    "packages/modules/adb": "0001-adb-specific-listener.patch",
    "frameworks/base": "0002-frameworks-base-tailscadble.patch",
    "packages/apps/Settings": "0003-settings-tailscadble.patch",
    "system/sepolicy": "0004-sepolicy-listen-property.patch",
}
EXPECTED_FILES = {
    "LICENSE",
    "NOTICE",
    "README.md",
    "TEST_PLAN.md",
    "THREAT_MODEL.md",
    "verify_export.py",
    *(f"patches/{name}" for name in PATCH_MAP.values()),
}


@dataclass(frozen=True)
class Inputs:
    requested: bool = False
    boot_completed: bool = False
    usb_debugging: bool = False
    lifecycle_ready: bool = False
    system_user: bool = True
    tailscale_package: bool = False
    live_vpn_interface: bool = False
    address_in_prefix: bool = False
    host_authorized: bool = False


def listener_enabled(state: Inputs) -> bool:
    return all((
        state.requested,
        state.boot_completed,
        state.usb_debugging,
        state.lifecycle_ready,
        state.system_user,
        state.tailscale_package,
        state.live_vpn_interface,
        state.address_in_prefix,
    ))


def shell_allowed(state: Inputs) -> bool:
    return listener_enabled(state) and state.host_authorized


def test_state_machine() -> None:
    stock = Inputs()
    assert not listener_enabled(stock)

    active = Inputs(True, True, True, True, True, True, True, True, True)
    assert listener_enabled(active) and shell_allowed(active)
    assert not shell_allowed(replace(active, host_authorized=False))

    for field in (
        "requested",
        "boot_completed",
        "usb_debugging",
        "lifecycle_ready",
        "system_user",
        "tailscale_package",
        "live_vpn_interface",
        "address_in_prefix",
    ):
        assert not listener_enabled(replace(active, **{field: False})), field

    # Physical underlay changes do not affect the decision while the validated VPN remains live.
    assert listener_enabled(active)
    # Service reconstruction clears owner intent; boot completion alone cannot re-arm it.
    rebooted = replace(active, requested=False, boot_completed=False)
    assert not listener_enabled(rebooted)
    assert not listener_enabled(replace(rebooted, boot_completed=True))


def added_lines(text: str) -> str:
    return "\n".join(
        line[1:] for line in text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def check_hunk_lengths(name: str, text: str) -> None:
    errors = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@", line)
        if not match:
            continue
        expected = tuple(int(value or 1) for value in match.groups())
        old = new = 0
        for body in lines[index + 1:]:
            if body.startswith("@@ ") or body.startswith("diff --git ") or body == "-- ":
                break
            if body.startswith("\\"):
                continue
            if not body or body[0] not in " +-":
                break
            old += body[0] != "+"
            new += body[0] != "-"
        if (old, new) != expected:
            errors.append(f"line {index + 1}: header {expected}, body {(old, new)}")
    assert not errors, f"invalid hunks in {name}: {'; '.join(errors)}"


def check_tree() -> None:
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert actual == EXPECTED_FILES, f"unexpected export files: {sorted(actual ^ EXPECTED_FILES)}"


def check_patches() -> None:
    texts = {name: (PATCHES / name).read_text(encoding="utf-8") for name in PATCH_MAP.values()}
    for name, text in texts.items():
        check_hunk_lengths(name, text)
    merged = "\n".join(texts.values())
    added = added_lines(merged)

    required = (
        "Tailscadble",
        "tailscadble_enabled",
        "service.adb.listen_addrs",
        "100.64.0.0/10",
        "com.tailscale.ipn",
        "onUserSwitching",
        "mTailscadbleLifecycleReady",
        "forceTailscadbleOff",
        "closeTailscadble(true)",
        "enforceControlPermissionOrInternalCaller",
        "system_adbd_prop",
        "network_address_server",
        "socket_spec_listen_connect_tcp_specific_ipv4",
    )
    for token in required:
        assert token in merged, f"missing invariant: {token}"

    forbidden_added = (
        "0.0.0.0",
        "ro.adb.secure",
        "persist.adb.tcp.port",
        "auth_required=false",
        "register_adb_tcp_service(CELL",
        "bound to \" + listenSpec",
        "<< addr",
        "%1$s:5555",
    )
    for token in forbidden_added:
        assert token not in added, f"forbidden added behavior: {token}"

    framework = texts[PATCH_MAP["frameworks/base"]]
    assert "CELLULAR" not in added_lines(framework)
    assert "TAILSCADBLE_SETTING, 0" in framework
    assert "UserHandle.USER_SYSTEM" in framework
    assert "vpnConfig.interfaze" in framework
    assert "properties.getInterfaceName()" in framework
    assert "Settings.Global.putInt(mContentResolver, TAILSCADBLE_SETTING, 0)" in framework
    assert "BroadcastReceiver" not in added_lines(framework)


def check_secrets() -> None:
    secret_patterns = (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\b(?:tskey|authkey)-[A-Za-z0-9_-]{8,}"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"(?i)\b(?:password|secret|token)\s*[:=]\s*[^<\s][^\s]{7,}"),
    )
    tailnet_ip = re.compile(r"\b100\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")

    for path in ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in secret_patterns:
            assert not pattern.search(text), f"possible secret in {path.name}: {pattern.pattern}"
        for match in tailnet_ip.finditer(text):
            address = IPv4Address(match.group(0))
            assert str(address) == "100.64.0.0", f"node-like address in {path.name}"


def check_patch_application(source_root: Path) -> None:
    for repo, patch_name in PATCH_MAP.items():
        subprocess.run(
            [
                "git",
                "-C",
                str(source_root / repo),
                "apply",
                "--check",
                "--cached",
                str(PATCHES / patch_name),
            ],
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    check_tree()
    check_patches()
    check_secrets()
    test_state_machine()
    if args.source_root:
        check_patch_application(args.source_root.resolve())
    print("TAILSCADBLE_EXPORT_OK")


if __name__ == "__main__":
    main()
