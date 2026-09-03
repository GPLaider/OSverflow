# Cellular Service Controls

OSverflow exposes two independent global controls while the subscription and
mobile-data service remain provisioned:

- **Call access** rejects ordinary outgoing cellular calls and hangs up ordinary
  incoming calls before InCall UI. Emergency calls and emergency callback mode
  remain available.
- **SMS access** fails outgoing point-to-point SMS before modem/IMS submission
  and acknowledges/discards incoming point-to-point SMS before app delivery.

They do not control application VoIP, RCS, MMS IP transfer, generic mobile data,
or cell-broadcast emergency alerts.

## Source anchors

| Patch/reference | Android project | Revision |
| --- | --- | --- |
| `0001-telephony-sms-access-gate.patch` | `frameworks/opt/telephony` | `21e2e9fc3cf0992bd91863aa33784ec5b24a806a` |
| `0002-teleservice-call-access-gate.patch` | `packages/services/Telephony` | `95e95093d0e9cca76b86906d414a7da6b95d45fe` |
| Settings controller and snippets | `packages/apps/Settings` | `adf61c13902a2789c965e6d74de5c466f5603b55` |

The Settings reference uses `Settings.Global` keys `osverflow_call_access` and
`osverflow_sms_access`, both defaulting to enabled. Copy the controller and merge
the two XML fragments into the downstream Settings resources; review product
policy and translations rather than applying them blindly.

These patches correspond to the accepted Lyriq implementation, but the portable
export has not been rebuilt as a standalone downstream patch stack. Carrier
behavior remains a physical-device acceptance gate.
