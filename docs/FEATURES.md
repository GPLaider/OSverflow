# Feature status

The labels below are intentionally strict:

- **device accepted**: exercised on the recorded signed Lyriq build;
- **public patch verified**: the exported files pass host/source checks;
- **reference only**: useful source is present, but this exact export is not a
  complete replayable Android integration;
- **excluded**: not part of the source RC or Lyriq RC1.

| Feature | Lyriq RC1 | Public package | Boundary |
| --- | --- | --- | --- |
| Verified Virtual A/B updates | device accepted | documented native AOSP path | No custom updater; exact release trust anchor required |
| USB data restriction | device accepted | upstream Lineage Trust reuse | No OSverflow fork unless upstream behavior changes |
| Inactivity reboot to BFU | device accepted | reference source + LineageParts patch | Opt-in; arms only after AFU, secure lock, whitelisted timeout |
| Disposable Space | device accepted | native-overlay recipe | Forced-ephemeral full guest; no custom deletion daemon |
| Compatibility Profiles | device accepted with empty catalog | reference source + service/UI patches | Exact package, signer, version, expiry, owned change IDs; no global weakening switch |
| Tailscadble | core path device accepted | public patch verified | Exact active Tailscale IPv4 listener; normal ADB authorization retained |
| Privacy Lock | device accepted | framework patch exported | OFF cannot be cleared by ordinary software reminder paths |
| Call access control | device accepted on recorded carrier path | TeleService patch + Settings reference | Ordinary cellular calls only; emergency path retained |
| SMS access control | device accepted on recorded carrier path | telephony patch + Settings reference | Point-to-point SMS transport; not RCS or generic IP data |
| CraftedG | separate OSverflow integration existed | host reference only | Stock KeyStore delegation only; no verdict/key/certificate manipulation |
| Hardware bring-up | device accepted on two XT2303-2 units | device metadata only | Proprietary blobs and full device tree are not redistributed here |

## Explicitly excluded

- eSIM experiments: no established EID/eUICC path in RC1.
- AVF/Fedora and protected-VM experiments.
- OVE cellular voice transformation: design only, not implemented.
- Duress credential work: not included in the frozen RC1 release contract.
- Play Integrity verdict manipulation, signature/build/SPL spoofing, keyboxes,
  certificate-chain replacement, private-key import, or signing private keys.
