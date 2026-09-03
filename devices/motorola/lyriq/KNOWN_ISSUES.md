# Known issues and unverified scope

- RC1 is `userdebug`, not a production `user` build.
- Framework SPL is `2026-06-01`; it must not be advertised as current.
- Public first installation and bootloader relocking are unsupported.
- Only XT2303-2 on `V1TLS35.73-60-3-14` is in scope.
- eSIM is excluded; no working EID/eUICC path was established.
- LG U+ registration, data, calling, and messaging were accepted. A KT-network
  MVNO registered and obtained data, but its IMS call path was not accepted.
  Retail KT, SKT, overseas carriers, VoNR, and Wi-Fi Calling remain unverified.
- Qi depends on correct coil alignment. Starting Qi with an already attached
  USB-C wired-audio accessory needs a controlled stock comparison.
- AVF/Fedora and protected VMs are excluded.
- Play Integrity, third-party keyboxes, and app compatibility are not guarantees.
- The exact Tailscadble export contains hardening newer than its recorded core
  device acceptance and still needs focused signed-build regression.
