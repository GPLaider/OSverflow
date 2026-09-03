#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'usage: %s <android-source-root>\n' "$0" >&2
  exit 2
fi

source_root=${1%/}
repo_root=$(cd "$(dirname "$0")/.." && pwd)

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

check_patch() {
  local project=$1 patch=$2
  git -C "$source_root/$project" apply --check --cached "$repo_root/$patch"
}

python3 "$repo_root/features/tailscadble/verify_export.py" \
  --source-root "$source_root"

check_head frameworks/base aaa4284f7e061771afb58c789924397111487e62
check_head packages/apps/Settings adf61c13902a2789c965e6d74de5c466f5603b55
check_head packages/apps/LineageParts df5dd9d53b01553168fd9c57e5c6b8bc8b4550c7
check_head frameworks/opt/telephony 21e2e9fc3cf0992bd91863aa33784ec5b24a806a
check_head packages/services/Telephony 95e95093d0e9cca76b86906d414a7da6b95d45fe

check_patch frameworks/base \
  features/privacy-lock/patches/0001-frameworks-base-privacy-lock.patch
check_patch frameworks/opt/telephony \
  features/cellular-service-controls/patches/0001-telephony-sms-access-gate.patch
check_patch packages/services/Telephony \
  features/cellular-service-controls/patches/0002-teleservice-call-access-gate.patch
check_patch packages/apps/LineageParts \
  features/security-suite-05678/patches/0001-lineageparts-inactivity-reboot-ui.patch
check_patch frameworks/base \
  features/security-suite-05678/patches/0002-frameworks-base-compatibility-profiles-service.patch
check_patch packages/apps/Settings \
  features/security-suite-05678/patches/0003-settings-compatibility-profiles-gateway.patch

printf '%s\n' OSVERFLOW_ANDROID_PATCHES_OK
