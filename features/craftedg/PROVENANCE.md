# CraftedG provenance and claim boundary

The public implementation is independently written against Java's public
`Provider` and `KeyStoreSpi` APIs. Its policy idea was isolated after reviewing
an OSverflow/Spacewar framework change at source revision
`316d75c131ede7e3f57fc12aae2cad1c7192df5d` and related GmsCompat work.

Relevant prior art and integration context include AOSP, GrapheneOS GmsCompat,
Universal SafetyNet Fix, PlayIntegrityFork, AxionOS, Evolution X, and
TrickyStore. Their code is not copied into this reference. Integrators must keep
their own upstream notices and licenses for any separately imported components.

Excluded from CraftedG:

- Play Integrity or attestation verdict changes;
- build, property, package-signature, or patch-level spoofing;
- keybox storage or selection;
- private-key import, certificate generation, chain replacement, or mutation;
- stack-trace substring checks as an authorization boundary; and
- claims of daemon/TEE isolation or Android device acceptance.

The trusted identity must be produced by Android framework package verification,
not by app-supplied text or configuration. Process-local means every caller in
that process can observe the wrapper; it is not per-call authorization.
