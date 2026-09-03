#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The OSverflow Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED = (
    "README.md",
    "LICENSE",
    "NOTICE",
    "docs/LICENSE_AUDIT.md",
    "SECURITY.md",
    "RELEASE_CHECKLIST.md",
    "devices/motorola/lyriq/support.json",
    "features/tailscadble/verify_export.py",
    "features/gmscompat/manifest.json",
    "features/gmscompat/NOTICE",
    "features/gmscompat/LICENSE.grapheneos-gmscompat",
    "features/craftedg/src/org/osverflow/craftedg/scopedkeystore/ScopedKeyStore.java",
    "features/craftedg/test/org/osverflow/craftedg/scopedkeystore/ScopedKeyStoreTest.java",
    "features/privacy-lock/patches/0001-frameworks-base-privacy-lock.patch",
    "features/cellular-service-controls/patches/0001-telephony-sms-access-gate.patch",
    "features/cellular-service-controls/patches/0002-teleservice-call-access-gate.patch",
    "features/cellular-service-controls/patches/0003-settings-cellular-service-controls.patch",
    "features/security-suite-05678/patches/0002-frameworks-base-inactivity-reboot.patch",
    "features/security-suite-05678/patches/0003-frameworks-base-compatibility-profiles.patch",
    "features/security-suite-05678/patches/0004-settings-compatibility-profiles.patch",
)

SPDX_REQUIRED = (
    "verify_release.py",
    "tools/verify_android_patches.sh",
    "features/tailscadble/verify_export.py",
    "features/craftedg/src/org/osverflow/craftedg/scopedkeystore/ScopedKeyStore.java",
    "features/craftedg/test/org/osverflow/craftedg/scopedkeystore/ScopedKeyStoreTest.java",
)

PATCH_SPDX_REQUIRED = (
    "features/cellular-service-controls/patches/0003-settings-cellular-service-controls.patch",
    "features/security-suite-05678/patches/0002-frameworks-base-inactivity-reboot.patch",
    "features/security-suite-05678/patches/0003-frameworks-base-compatibility-profiles.patch",
    "features/security-suite-05678/patches/0004-settings-compatibility-profiles.patch",
)

FORBIDDEN_SUFFIXES = {
    ".img", ".bin", ".zip", ".apk", ".apex", ".pk8", ".pem", ".key",
    ".p12", ".pfx", ".jks", ".keystore", ".der", ".class",
}

TEXT_PATTERNS = (
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"LPA:1\$", re.IGNORECASE), "eSIM activation code"),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE), "local Windows path"),
    (re.compile(r"/mnt/(?:buildrouter|[a-z])/(?:Users/)?[^\s]+", re.IGNORECASE), "local build path"),
    (re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{160,}={0,2}(?![A-Za-z0-9+/])"), "long base64 payload"),
    (re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{96,}(?![0-9A-Fa-f])"), "long hex payload"),
)

GMSCOMPAT_FORBIDDEN = (
    "GmsCompatIntegrity",
    "PifKeyStore",
    "PlayIntegritySpoof",
    "TrickyStore",
    "KeyBox",
    "CertificateHacker",
    "spoofBuild",
    "spoofSignature",
    "ro.build.version.security_patch",
)


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stdout}")
    return result.stdout


def verify_tree() -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            raise SystemExit(f"missing required file: {relative}")

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            raise SystemExit(f"symlink not allowed: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise SystemExit(f"binary/key artifact not allowed: {relative}")
        data = path.read_bytes()
        if b"\x00" in data:
            raise SystemExit(f"binary content not allowed: {relative}")
        text = data.decode("utf-8")
        for pattern, label in TEXT_PATTERNS:
            if pattern.search(text):
                raise SystemExit(f"{label} detected in {relative}")

    for patch in ROOT.rglob("*.patch"):
        if "diff --git " not in patch.read_text(encoding="utf-8"):
            raise SystemExit(f"invalid or empty patch: {patch.relative_to(ROOT)}")


def verify_device_metadata() -> None:
    support = json.loads(
        (ROOT / "devices/motorola/lyriq/support.json").read_text(encoding="utf-8")
    )
    assert support["device"]["codename"] == "lyriq"
    assert support["device"]["models"] == ["XT2303-2"]
    assert support["support_status"] == "release-candidate"
    assert support["required_stock_baseline"] == "V1TLS35.73-60-3-14"
    assert support["hardware_prebuilt_source_build"] == "V1TLS35.73-60-3-10/40dcc-72d036"
    assert support["stock_input_contracts"] == [
        "V1TLS35.73-60-3-10/40dcc-72d036",
        "V1TLS35.73-60-3-14/89e5f-45c91",
    ]
    device_source_repository = "https://github.com/GPLaider/android_device_motorola_lyriq"
    device_source_commit = "cfa09263aeac686f9ef6fb963dc5bd4d31eec4c2"
    assert support["device_source_repository"] == device_source_repository
    assert support["device_source_commit"] == device_source_commit
    assert support["stock_input_extractor"] == (
        f"{device_source_repository}/blob/{device_source_commit}/tools/extract_stock.py"
    )
    assert support["kernel_source_reference"] == (
        f"{device_source_repository}/blob/{device_source_commit}/kernel-source-reference.json"
    )
    assert support["bootloader"]["unlock_required"] is True
    assert support["bootloader"]["relocking_supported"] is False
    assert support["public_install_artifact"] is None


def verify_spdx() -> None:
    for relative in SPDX_REQUIRED:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "SPDX-License-Identifier: Apache-2.0" not in text:
            raise SystemExit(f"missing Apache-2.0 SPDX identifier: {relative}")
    for relative in PATCH_SPDX_REQUIRED:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "+ * SPDX-License-Identifier: Apache-2.0" not in text:
            raise SystemExit(f"missing Apache-2.0 SPDX marker in added patch source: {relative}")


def verify_tailscadble() -> None:
    output = run(sys.executable, "verify_export.py", cwd=ROOT / "features/tailscadble")
    if "TAILSCADBLE_EXPORT_OK" not in output:
        raise SystemExit("Tailscadble verifier did not report success")


def verify_gmscompat() -> None:
    root = ROOT / "features/gmscompat"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != 1
        or manifest.get("status") != "upstream-derived-source-rc"
        or manifest.get("lineage_manifest_commit")
        != "5c3bbcbf9364c096cbe9a361af998e0bc398bdc6"
    ):
        raise SystemExit("invalid GmsCompat source manifest identity")

    patches = manifest.get("patches")
    if not isinstance(patches, list) or len(patches) != 16:
        raise SystemExit("unexpected GmsCompat patch count")
    projects: set[str] = set()
    for entry in patches:
        project = entry.get("project")
        relative = entry.get("patch")
        digest = entry.get("sha256")
        if not isinstance(project, str) or project in projects:
            raise SystemExit(f"invalid or duplicate GmsCompat project: {project}")
        if not isinstance(relative, str) or not relative.startswith("patches/"):
            raise SystemExit(f"invalid GmsCompat patch path: {relative}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise SystemExit(f"invalid GmsCompat patch digest: {relative}")
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"GmsCompat patch digest mismatch: {relative}")
        text = path.read_text(encoding="utf-8")
        for marker in GMSCOMPAT_FORBIDDEN:
            if marker.lower() in text.lower():
                raise SystemExit(f"excluded GmsCompat material in {relative}: {marker}")
        projects.add(project)

    if manifest.get("companions") != [
        {
            "project": "external/GmsCompatConfig",
            "repository": "https://github.com/GrapheneOS/platform_external_GmsCompatConfig",
            "commit": "87b8bc336cc6aca7fe480cfcc98aaaeecfd7eb6a",
            "version": 170,
            "apk_sha256": "1cab0f533caefcbf49c7c9de1b4399b3b518a5e4c91ca98c4c7cf4fd363d986d",
            "certificate_sha256": "6ebb65c5daa95641f7a774ea35d26ff251575cb32e34a8a5d655b2742b57321f",
        }
    ]:
        raise SystemExit("unexpected GmsCompat companion source contract")


def verify_craftedg() -> None:
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java:
        raise SystemExit("JDK 17+ javac/java are required")
    source = ROOT / "features/craftedg/src/org/osverflow/craftedg/scopedkeystore/ScopedKeyStore.java"
    test = ROOT / "features/craftedg/test/org/osverflow/craftedg/scopedkeystore/ScopedKeyStoreTest.java"
    with tempfile.TemporaryDirectory(prefix="osverflow-craftedg-") as output_dir:
        run(javac, "-Xlint:all", "-d", output_dir, str(source), str(test))
        result = run(
            java,
            "-ea",
            "-cp",
            output_dir,
            "org.osverflow.craftedg.scopedkeystore.ScopedKeyStoreTest",
        )
    if "CRAFTEDG_CHECKS_OK" not in result:
        raise SystemExit("CraftedG assertion test did not report success")


def main() -> None:
    verify_tree()
    verify_device_metadata()
    verify_spdx()
    verify_tailscadble()
    verify_gmscompat()
    verify_craftedg()
    print("OSVERFLOW_RELEASE_SOURCE_OK")


if __name__ == "__main__":
    main()
