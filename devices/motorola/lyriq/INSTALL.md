# Installation boundary

There is currently no public first-install artifact.

The frozen RC1 is qualified only as a local full Virtual A/B update from an
already compatible OSverflow installation that trusts the same OTA certificate.
Stock recovery does not trust that certificate, and improvising a partition list
from an OTA can leave mismatched AVB metadata or an unbootable slot.

Before public installation instructions are added, the spare XT2303-2 must pass a
clean install from `V1TLS35.73-60-3-14`, normal boot, feature smoke tests, failed-
update recovery, and rollback using the exact published files. Bootloader
relocking remains unsupported.
