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
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LYRIQ_PLATFORM_SUPPORT = ROOT / "features/lyriq-platform-support/manifest.json"
LYRIQ_LOCAL_MANIFEST = ROOT / "devices/motorola/lyriq/local_manifests/osverflow-lyriq.xml"

REQUIRED = (
    "README.md",
    "LICENSE",
    "NOTICE",
    "docs/LICENSE_AUDIT.md",
    "SECURITY.md",
    "RELEASE_CHECKLIST.md",
    "devices/motorola/lyriq/support.json",
    "devices/motorola/lyriq/local_manifests/osverflow-lyriq.xml",
    "features/lyriq-platform-support/manifest.json",
    "features/lyriq-platform-support/NOTICE",
    "features/lyriq-platform-support/LICENSE.libsepol",
    "features/lyriq-platform-support/LICENSE.dng_sdk",
    "features/lyriq-platform-support/LICENSE.libjxl",
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
    device_source_commit = "625368f36475fbf26a6aff624725c1abeeed5311"
    assert support["device_source_repository"] == device_source_repository
    assert support["device_source_commit"] == device_source_commit
    assert support["stock_input_extractor"] == (
        f"{device_source_repository}/blob/{device_source_commit}/tools/extract_stock.py"
    )
    assert support["kernel_source_reference"] == (
        f"{device_source_repository}/blob/{device_source_commit}/kernel-source-reference.json"
    )
    assert support["source_manifest"] == {
        "lineage_repository": "https://github.com/LineageOS/android",
        "lineage_commit": "5c3bbcbf9364c096cbe9a361af998e0bc398bdc6",
        "local_manifest": "local_manifests/osverflow-lyriq.xml",
        "platform_support_manifest": "../../../features/lyriq-platform-support/manifest.json",
    }
    assert support["bootloader"]["unlock_required"] is True
    assert support["bootloader"]["relocking_supported"] is False
    assert support["build"]["type"] == "user"
    assert support["public_install_artifact"] is None


def verify_lyriq_platform_support() -> None:
    manifest = json.loads(LYRIQ_PLATFORM_SUPPORT.read_text(encoding="utf-8"))
    expected = {
        "build/make": (
            "5a841be38fec92de9a8a408cf5812ca748ccc02e",
            "patches/0001-build-make-preserve-hybrid-payloads.patch",
            "f4f067477f5efbc44dc953e4ee77436d96adb9ef15e35f63f9e70b109b2c0c8b",
            "Apache-2.0",
        ),
        "device/lineage/sepolicy": (
            "c6e972cf4ff9bd472052b29cf8eae7bc3e70d378",
            "patches/0002-lineage-sepolicy-avoid-stock-camera-property-duplicate.patch",
            "2c54ed183416acddd9a44297cb1b9eba48a421202bb7dc269748b144ab725919",
            "Apache-2.0",
        ),
        "external/selinux": (
            "085c131ad1b984bfa8ffdafee7a976e9d89f403c",
            "patches/0003-libsepol-merge-cil-xperm-rules.patch",
            "a58760d89da554cb445b57fa2e1542a7e505ce63a6f3e9242b15e133c37fbe55",
            "LGPL-2.1-only",
        ),
        "packages/modules/Telephony": (
            "6175c04a2cb3254455c58c9c653dc36a8a7e6dac",
            "patches/0004-telephony-metrics-vendor-compat-shim.patch",
            "a9009d6eb8e143999310c632c71c67c331b78b78e729e10e0079712fce9588ef",
            "Apache-2.0",
        ),
        "external/dng_sdk": (
            "60de57ba9f18dd6366914ad74580063fe102c87c",
            "patches/0005-dng-sdk-avoid-vendor-variant.patch",
            "7173f9b12a051b5db2e3d440358cff2777544c346e2f292d3c12b1367e554a19",
            "LicenseRef-Adobe-DNG-SDK",
        ),
        "external/libjxl": (
            "4365ed52860edc6898277200c9bb41971f005e11",
            "patches/0006-libjxl-avoid-vendor-variant.patch",
            "1a8ee7060161167738760ce789612cf3d2a33753115d3b6a27059c8db9e58117",
            "BSD-3-Clause",
        ),
    }
    if (
        manifest.get("schema") != 1
        or manifest.get("status") != "source-closure-rc"
        or manifest.get("lineage_manifest_commit")
        != "5c3bbcbf9364c096cbe9a361af998e0bc398bdc6"
    ):
        raise SystemExit("invalid Lyriq platform-support manifest identity")
    entries = manifest.get("patches")
    if not isinstance(entries, list) or len(entries) != len(expected):
        raise SystemExit("unexpected Lyriq platform-support patch count")
    seen: set[str] = set()
    for entry in entries:
        project = entry.get("project")
        if not isinstance(project, str) or project in seen or project not in expected:
            raise SystemExit(f"invalid Lyriq platform-support project: {project}")
        base, relative, digest, license_id = expected[project]
        if entry != {
            "project": project,
            "base": base,
            "patch": relative,
            "sha256": digest,
            "license": license_id,
        }:
            raise SystemExit(f"unexpected Lyriq platform-support contract: {project}")
        path = LYRIQ_PLATFORM_SUPPORT.parent / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Lyriq platform-support patch mismatch: {relative}")
        seen.add(project)

    root = ElementTree.parse(LYRIQ_LOCAL_MANIFEST).getroot()
    remotes = {item.get("name"): item.get("fetch") for item in root.findall("remote")}
    if remotes != {
        "osverflow-github": "https://github.com/",
        "osverflow-aosp": "https://android.googlesource.com/",
    }:
        raise SystemExit("unexpected Lyriq local-manifest remotes")
    projects = {
        item.get("path"): (
            item.get("name"), item.get("remote"), item.get("revision")
        )
        for item in root.findall("project")
    }
    if projects != {
        "device/motorola/lyriq": (
            "GPLaider/android_device_motorola_lyriq",
            "osverflow-github",
            "625368f36475fbf26a6aff624725c1abeeed5311",
        ),
        "packages/apps/GmsCompat": (
            "VoltageOS/packages_apps_GmsCompat",
            "osverflow-github",
            "ec541b9f7ff42faad5aa553e4bb255014aec2527",
        ),
        "external/GmsCompatConfig": (
            "GrapheneOS/platform_external_GmsCompatConfig",
            "osverflow-github",
            "87b8bc336cc6aca7fe480cfcc98aaaeecfd7eb6a",
        ),
        "packages/apps/Calendar": (
            "platform/packages/apps/Calendar",
            "osverflow-aosp",
            "03e057090a3a1e99c1e1e6c495f7a79aa0719b3a",
        ),
    }:
        raise SystemExit("unexpected Lyriq local-manifest project pins")


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
    verify_lyriq_platform_support()
    verify_spdx()
    verify_tailscadble()
    verify_gmscompat()
    verify_craftedg()
    print("OSVERFLOW_RELEASE_SOURCE_OK")


if __name__ == "__main__":
    main()
