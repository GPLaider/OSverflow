# Lyriq platform support

This series closes the device-specific gaps between a clean LineageOS 23.2
checkout and the accepted Motorola Edge 40 (`lyriq`) hybrid build graph.

It preserves the stock boot and vendor payloads during target-files signing,
avoids the duplicate stock camera property context, merges extended SELinux
permissions into the imported policy, supplies the legacy telephony metrics
surface required by the stock IMS stack, and prevents duplicate vendor library
variants already supplied by the stock vendor image.

Every patch is bound to the exact project base and SHA-256 in `manifest.json`.
The Lyriq local manifest pins every patched Android project to those verified
bases instead of relying on moving Lineage branch tips.
`build/soong` and `vendor/lineage` workspace workarounds are intentionally not
included because they are not part of the Lyriq product contract.

The series has source-level acceptance only until a clean production `user`
target-files build and post-signing partition audit pass.
