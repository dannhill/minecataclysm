# ADR-002: semantic CWM boundary between processes

Status: ACCEPTED (original specification §8, §21–29; amendments §3, §6–13).

Keep CDDA and Luanti in separate processes. CWM carries engine-neutral
semantic data, immutable projections, commands and acknowledgements. Use
4-byte big-endian framing and verify FlatBuffers before dereferencing fields.
The abstract transport, session identity, message sequencing and resync state
machine are architectural requirements; Unix sockets are the initial backend.

Record observed schema separately from required schema. Protocol remediation
requires an explicit version transition, regenerated bindings and rejected
incompatible handshakes. Do not silently reorder enums or union tags.

This technical boundary does not independently establish licensing compliance.
Asset provenance and notices must be audited against the pinned source files.
