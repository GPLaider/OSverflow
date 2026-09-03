#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 The OSverflow Project
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

mode=verify
if [[ $# -eq 2 && $1 == --apply ]]; then
  mode=apply
  shift
elif [[ $# -eq 2 && $1 == --check-applied ]]; then
  mode=check-applied
  shift
elif [[ $# -ne 1 || $1 == --* ]]; then
  printf 'usage: %s [--apply|--check-applied] <android-source-root>\n' "$0" >&2
  exit 2
fi

source_root=${1%/}
repo_root=$(cd "$(dirname "$0")/.." && pwd)

[[ -d $source_root ]]
if [[ $mode != verify ]]; then
  [[ -x $source_root/.repo/repo/repo ]]
fi
if [[ $mode == apply ]]; then
  current_dirty=$(cd "$source_root" && .repo/repo/repo forall -c \
    'if ! git diff --quiet || ! git diff --cached --quiet || test -n "$(git ls-files --others --exclude-standard)"; then printf "%s\n" "$REPO_PATH"; fi' \
    | sort)
  if [[ -n $current_dirty ]]; then
    printf 'refusing to apply to a dirty Android checkout:\n%s\n' "$current_dirty" >&2
    exit 1
  fi
fi

check_head() {
  local project=$1 expected=$2
  local actual
  actual=$(git -C "$source_root/$project" rev-parse HEAD)
  if [[ $actual != "$expected" ]]; then
    printf 'unexpected %s HEAD: %s (expected %s)\n' \
      "$project" "$actual" "$expected" >&2
    exit 1
  fi
}

temp_root=$(mktemp -d)
trap 'rm -rf "$temp_root"' EXIT

check_series() {
  local project=$1
  shift
  local clone="$temp_root/${project//\//_}.repo"
  git clone --shared --no-checkout --quiet "$source_root/$project" "$clone"
  git -C "$clone" checkout --quiet "$(git -C "$source_root/$project" rev-parse HEAD)"
  for patch in "$@"; do
    printf 'APPLY\t%s\t%s\n' "$project" "$patch"
    git -C "$clone" apply --index "$repo_root/$patch"
    git -C "$clone" diff --cached --check
    git -C "$clone" -c user.name=OSverflow -c user.email=noreply@osverflow.invalid \
      commit --quiet -m "verify $patch"
  done

  if [[ $mode != verify ]]; then
    local target="$source_root/$project"
    local expected_tree actual_tree
    expected_tree=$(git -C "$clone" write-tree)
    if [[ $mode == apply ]]; then
      if [[ -n $(git -C "$target" status --porcelain) ]]; then
        printf 'refusing to apply to dirty project: %s\n' "$project" >&2
        exit 1
      fi
      for patch in "$@"; do
        git -C "$target" apply --index "$repo_root/$patch"
      done
    fi
    git -C "$target" diff --cached --check
    if git -C "$target" diff --cached --quiet; then
      printf 'missing applied patch series: %s\n' "$project" >&2
      exit 1
    fi
    git -C "$target" diff --quiet
    [[ -z $(git -C "$target" ls-files --others --exclude-standard) ]]
    actual_tree=$(git -C "$target" write-tree)
    if [[ $actual_tree != "$expected_tree" ]]; then
      printf 'applied tree mismatch: %s\n' "$project" >&2
      exit 1
    fi
  fi
}

python3 "$repo_root/features/tailscadble/verify_export.py"

check_head frameworks/base aaa4284f7e061771afb58c789924397111487e62
check_head packages/apps/Settings adf61c13902a2789c965e6d74de5c466f5603b55
check_head packages/apps/LineageParts df5dd9d53b01553168fd9c57e5c6b8bc8b4550c7
check_head frameworks/opt/telephony 21e2e9fc3cf0992bd91863aa33784ec5b24a806a
check_head packages/services/Telephony 95e95093d0e9cca76b86906d414a7da6b95d45fe
check_head art 1690c6912a7972c9e62c39b48c706de9b8b18b4a
check_head bionic 7ad2441de12bf7b5dc0055e0a940583d80fe104b
check_head frameworks/native 9a9d8be6865c1d6ebd10321375b082314de5ecf6
check_head libcore 1c599b67bcd3de5c50c79d0622e40b6de99b4cb4
check_head packages/modules/AppSearch 66fdb746655f01346649c34d380faf5dad593b98
check_head packages/modules/Bluetooth b5d4b73e1122a714c3c5223b9932c7b733690c5d
check_head packages/modules/ConfigInfrastructure 0c59a9196a09ef1f02571d10525e2cb1d2b8fc53
check_head packages/modules/Connectivity c9f3e7795256bd4a3f99d02e604e24fd1552c2b3
check_head packages/modules/Nfc 393ad5d17936a27b241f2796ff58f877ee9062aa
check_head packages/modules/Permission ee30155a8872cd022b5b7fb1983fdcf09e752723
check_head packages/modules/StatsD aae39057403d4538cb56c856b880fd02d5765a1e
check_head packages/providers/DownloadProvider 6d2a304dc8237b2da9910799380636fe5b1f3970
check_head system/tools/aidl 3747384b876442e7ea0c355fe5adc75b29362833
check_head packages/modules/adb 262cc9ada912c17f30f3130ae22e8012be4e10fe
check_head system/sepolicy 885cc500f6078a766d1f6def5ce4c06c55841773
check_head packages/apps/GmsCompat ec541b9f7ff42faad5aa553e4bb255014aec2527
check_head build/make 5a841be38fec92de9a8a408cf5812ca748ccc02e
check_head device/lineage/sepolicy c6e972cf4ff9bd472052b29cf8eae7bc3e70d378
check_head external/selinux 085c131ad1b984bfa8ffdafee7a976e9d89f403c
check_head packages/modules/Telephony 6175c04a2cb3254455c58c9c653dc36a8a7e6dac
check_head external/dng_sdk 60de57ba9f18dd6366914ad74580063fe102c87c
check_head external/libjxl 4365ed52860edc6898277200c9bb41971f005e11

check_series frameworks/base \
  features/gmscompat/patches/0003-frameworks-base.patch \
  features/tailscadble/patches/0002-frameworks-base-tailscadble.patch \
  features/privacy-lock/patches/0001-frameworks-base-privacy-lock.patch \
  features/security-suite-05678/patches/0002-frameworks-base-inactivity-reboot.patch \
  features/security-suite-05678/patches/0003-frameworks-base-compatibility-profiles.patch
check_series frameworks/opt/telephony \
  features/cellular-service-controls/patches/0001-telephony-sms-access-gate.patch
check_series packages/services/Telephony \
  features/cellular-service-controls/patches/0002-teleservice-call-access-gate.patch
check_series packages/apps/Settings \
  features/gmscompat/patches/0006-settings.patch \
  features/tailscadble/patches/0003-settings-tailscadble.patch \
  features/cellular-service-controls/patches/0003-settings-cellular-service-controls.patch \
  features/security-suite-05678/patches/0004-settings-compatibility-profiles.patch
check_series packages/apps/LineageParts \
  features/security-suite-05678/patches/0001-lineageparts-inactivity-reboot-ui.patch
check_series art features/gmscompat/patches/0001-art.patch
check_series bionic features/gmscompat/patches/0002-bionic.patch
check_series frameworks/native features/gmscompat/patches/0004-frameworks-native.patch
check_series libcore features/gmscompat/patches/0005-libcore.patch
check_series packages/modules/AppSearch features/gmscompat/patches/0007-appsearch.patch
check_series packages/modules/Bluetooth features/gmscompat/patches/0008-bluetooth.patch
check_series packages/modules/ConfigInfrastructure \
  features/gmscompat/patches/0009-config-infrastructure.patch
check_series packages/modules/Connectivity features/gmscompat/patches/0010-connectivity.patch
check_series packages/modules/Nfc features/gmscompat/patches/0011-nfc.patch
check_series packages/modules/Permission features/gmscompat/patches/0012-permission.patch
check_series packages/modules/StatsD features/gmscompat/patches/0013-statsd.patch
check_series packages/providers/DownloadProvider \
  features/gmscompat/patches/0014-download-provider.patch
check_series system/tools/aidl features/gmscompat/patches/0015-aidl.patch
check_series packages/modules/adb features/tailscadble/patches/0001-adb-specific-listener.patch
check_series system/sepolicy features/tailscadble/patches/0004-sepolicy-listen-property.patch
check_series packages/apps/GmsCompat \
  features/gmscompat/patches/0016-gmscompat-app-lineage-adapter.patch
check_series build/make \
  features/lyriq-platform-support/patches/0001-build-make-preserve-hybrid-payloads.patch
check_series device/lineage/sepolicy \
  features/lyriq-platform-support/patches/0002-lineage-sepolicy-avoid-stock-camera-property-duplicate.patch
check_series external/selinux \
  features/lyriq-platform-support/patches/0003-libsepol-merge-cil-xperm-rules.patch
check_series packages/modules/Telephony \
  features/lyriq-platform-support/patches/0004-telephony-metrics-vendor-compat-shim.patch
check_series external/dng_sdk \
  features/lyriq-platform-support/patches/0005-dng-sdk-avoid-vendor-variant.patch
check_series external/libjxl \
  features/lyriq-platform-support/patches/0006-libjxl-avoid-vendor-variant.patch

if [[ $mode != verify ]]; then
  expected=$(printf '%s\n' \
    art bionic build/make device/lineage/sepolicy external/dng_sdk \
    external/libjxl external/selinux frameworks/base frameworks/native \
    frameworks/opt/telephony libcore packages/apps/GmsCompat \
    packages/apps/LineageParts packages/apps/Settings packages/modules/AppSearch \
    packages/modules/Bluetooth packages/modules/ConfigInfrastructure \
    packages/modules/Connectivity packages/modules/Nfc packages/modules/Permission \
    packages/modules/StatsD packages/modules/Telephony packages/modules/adb \
    packages/providers/DownloadProvider packages/services/Telephony system/sepolicy \
    system/tools/aidl | sort)
  actual=$(cd "$source_root" && .repo/repo/repo forall -c \
    'if ! git diff --quiet || ! git diff --cached --quiet || test -n "$(git ls-files --others --exclude-standard)"; then printf "%s\n" "$REPO_PATH"; fi' \
    | sort)
  [[ $actual == "$expected" ]]
  if [[ $mode == apply ]]; then
    printf '%s\n' OSVERFLOW_ANDROID_PATCHES_APPLIED_OK
  else
    printf '%s\n' OSVERFLOW_ANDROID_PATCHES_MATCH_OK
  fi
else
  printf '%s\n' OSVERFLOW_ANDROID_PATCHES_OK
fi
