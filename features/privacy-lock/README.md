# Privacy Lock

This patch turns the existing per-user camera, microphone, and location OFF
states into fail-closed software locks:

- blocked camera/microphone requests do not launch an unblock reminder;
- ordinary software callers cannot clear a software sensor lock;
- location OFF has no provider, allowlist, ADAS, or ignore-settings exception;
- location ON is accepted only from the one-shot system Settings changer path.

The user-facing Settings and Quick Settings controls remain the existing Android
controls. This patch changes the service-layer authority behind them.

## Source anchor

- Android project: `frameworks/base`
- revision: `aaa4284f7e061771afb58c789924397111487e62`
- patch: `patches/0001-frameworks-base-privacy-lock.patch`

Check against a clean index:

```text
git -C frameworks/base apply --check --cached <export>/patches/0001-frameworks-base-privacy-lock.patch
```

The patch was separated from the implementation used by the accepted Lyriq RC1.
This exact export still requires a clean build and focused device regression
before another ROM may claim equivalent acceptance.

The lock is software policy, not a physical sensor disconnect. The accepted
OSverflow policy deliberately has no emergency-call unlock exception; downstream
projects must disclose any policy change rather than silently weakening it.
