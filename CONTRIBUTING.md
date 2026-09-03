# Contributing

Keep changes small, attributable, and independently testable.

1. State the exact Android project and source revision a patch targets.
2. Preserve upstream copyright, license, and NOTICE material.
3. Add the smallest check that fails when the changed security boundary breaks.
4. Separate host checks, build success, package verification, and physical-device
   acceptance. None substitutes for another.
5. Never add signing private keys, keyboxes, credentials, device/subscriber
   identifiers, activation codes, proprietary partition images, or private logs.
6. Do not claim official project affiliation or hardware support from a compile.

AI-assisted contributions are allowed only when the human contributor reviews
the exact diff, supplies real verification evidence, and remains accountable for
licensing, security, privacy, and correctness. Fabricated tests or device results
are grounds for rejection.

Run `python verify_release.py` before submitting a change.
