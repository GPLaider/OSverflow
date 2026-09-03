# CraftedG

CraftedG is OSverflow's public reference for installing a process-local
`AndroidKeyStore` provider wrapper only when all of these framework-trusted
inputs match:

- sandboxed GMS compatibility is enabled;
- the package identity was verified by the framework; and
- the exact target process name matches.

Every exported `KeyStoreSpi` operation delegates to the supplied stock SPI.
Non-target callers return before the JCA provider registry is inspected or
changed. Missing delegates, unexpected provider state, or installation failure
fail closed.

This is a JDK reference, not a complete Android integration. It does not modify
keys, certificates, build identity, package signatures, patch levels, system
properties, or service verdicts. It contains no keybox or private material.

## Check

With JDK 17 or newer:

```text
javac -Xlint:all -d out src/org/osverflow/craftedg/scopedkeystore/ScopedKeyStore.java test/org/osverflow/craftedg/scopedkeystore/ScopedKeyStoreTest.java
java -ea -cp out org.osverflow.craftedg.scopedkeystore.ScopedKeyStoreTest
```

Expected output: `CRAFTEDG_CHECKS_OK`.

Read [PROVENANCE.md](PROVENANCE.md) before Android integration.
